# LiveDrop System Design (by Karl Sassine)
https://excalidraw.com/#json=OO_QnekBFOuEKMr2EbubC,stwHfFdGHrabM0-7XPRQRg

## Architecture Overview


This document outlines the system design for LiveDrop, a flash-sale and follow platform that enables creators to run limited-inventory live product drops with real-time notifications and high-concurrency order processing.

## High-Level Architecture

### Client Layer
- **Mobile App & Web App**: Primary user interfaces for browsing, following creators, and placing orders
- **CDN**: Content delivery network for static assets, product images, and cached content to reduce latency

### API Gateway & Load Balancing
- **Load Balancer**: Distributes incoming requests across multiple service instances
- **API Gateway**: Single entry point providing authentication, rate limiting, request routing, and API versioning

### Microservices Architecture

The system is decomposed into specialized microservices, each handling specific domains:

#### Core Services
- **Auth Service**: User authentication, authorization, and session management
- **Creator Service**: Creator profiles, product catalog management
- **Follow Service**: Follow/unfollow relationships, follower lists with pagination
- **Order Service**: Order processing, inventory management, idempotency handling
- **Drop Service**: Drop scheduling, lifecycle management (upcoming/live/ended states)
- **Inventory Service**: Real-time stock tracking, overselling prevention
- **Notification Service**: Real-time push notifications for drop events
- **Search Service**: Product discovery, filtering, and pagination
- **Audit Trail Service**: Order history, transaction logging

#### Supporting Services
- **Payment Gateway**: External payment processing integration

### Data Storage & Caching
- **Primary Database**: Relational database for transactional data (PostgreSQL)
- **Redis Cache**: High-performance caching for frequently accessed data
- **S3 Storage**: Static file storage for product images and assets
- **Elasticsearch**: Full-text search and complex product filtering

### Message Queue & Real-time Communication
- **Message Queue (Kafka)**: Asynchronous event processing for notifications and inventory updates
- **WebSocket**: Real-time bidirectional communication for live drop updates

## Data Model Design

### Database Architecture Strategy

The data model uses a hybrid approach combining different database technologies optimized for specific use cases:

- **PostgreSQL + Read Replicas**: Primary transactional data with read scaling
- **Sharded PostgreSQL**: Follow relationships partitioned by creator_id for celebrity scalability
- **Redis Cluster**: High-performance inventory tracking and caching
- **ClickHouse (Columnar)**: Analytics and event tracking for business intelligence

### Core Entities

```sql
-- Users (PostgreSQL + Read Replicas)
users (
  user_id PRIMARY KEY,
  email UNIQUE NOT NULL,
  username UNIQUE NOT NULL,  
  password_hash NOT NULL,
  profile_image_url,
  created_at,
  updated_at,
  is_active BOOLEAN DEFAULT true
)

-- Creators (PostgreSQL + Read Replicas) 
creators (
  creator_id PRIMARY KEY,
  user_id FOREIGN KEY REFERENCES users(user_id),
  creator_name NOT NULL,
  bio TEXT,
  profile_image_url,
  follower_count INTEGER DEFAULT 0, -- cached/denormalized
  total_drops INTEGER DEFAULT 0,
  is_verified BOOLEAN DEFAULT false,
  created_at,
  updated_at
)

-- Products (PostgreSQL + Read Replicas)
products (
  product_id PRIMARY KEY,
  creator_id FOREIGN KEY REFERENCES creators(creator_id),
  name NOT NULL,
  description TEXT,
  base_price DECIMAL(10,2),
  images_urls JSONB, -- Array of image URLs
  category VARCHAR(50),
  created_at,
  updated_at,
  is_active BOOLEAN DEFAULT true
)

-- Follow Relationships (Sharded PostgreSQL by creator_id)
-- Shard key: creator_id for efficient celebrity creator queries
follows (
  follow_id PRIMARY KEY,
  user_id INTEGER NOT NULL,
  creator_id INTEGER NOT NULL, -- SHARDING KEY
  created_at,
  status ENUM('active', 'inactive'),
  UNIQUE(user_id, creator_id)
)

-- Follower Stats per Shard (materialized view for performance)
follower_stats (
  creator_id PRIMARY KEY,
  follower_count INTEGER,
  last_updated TIMESTAMP
)

-- Drops (PostgreSQL + Read Replicas)
drops (
  drop_id PRIMARY KEY,
  creator_id FOREIGN KEY REFERENCES creators(creator_id),
  name NOT NULL,
  description TEXT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  status ENUM('scheduled', 'live', 'ended'),
  total_inventory INTEGER,
  remaining_inventory INTEGER, -- cached from Redis
  low_stock_threshold INTEGER DEFAULT 10,
  created_at,
  updated_at
)

-- Drop Items (individual products in a drop)
drop_items (
  drop_id FOREIGN KEY REFERENCES drops(drop_id),
  product_id FOREIGN KEY REFERENCES products(product_id),
  variant_id INTEGER, -- for size/color variations
  drop_price DECIMAL(10,2),
  initial_stock INTEGER,
  current_stock INTEGER, -- cached from Redis for display
  PRIMARY KEY(drop_id, product_id, variant_id)
)

-- Orders (Partitioned PostgreSQL by created_at for performance)
orders (
  order_id PRIMARY KEY,
  user_id FOREIGN KEY REFERENCES users(user_id),
  drop_id FOREIGN KEY REFERENCES drops(drop_id),
  product_id FOREIGN KEY REFERENCES products(product_id),
  variant_id INTEGER,
  quantity INTEGER,
  unit_price DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  order_status ENUM('pending', 'confirmed', 'cancelled', 'shipped'),
  idempotency_key VARCHAR(255) UNIQUE, -- prevent duplicate orders
  created_at, -- PARTITION KEY (monthly partitions)
  updated_at
)

-- Order Items (for multi-item orders)
order_items (
  item_id PRIMARY KEY,
  order_id FOREIGN KEY REFERENCES orders(order_id),
  product_id FOREIGN KEY REFERENCES products(product_id),
  variant_id INTEGER,
  quantity INTEGER,
  unit_price DECIMAL(10,2),
  total_price DECIMAL(10,2)
)

-- Payment Records
payments (
  payment_id PRIMARY KEY,
  order_id FOREIGN KEY REFERENCES orders(order_id),
  payment_method ENUM('card', 'paypal', 'apple_pay'),
  amount DECIMAL(10,2),
  currency CHAR(3) DEFAULT 'USD',
  payment_provider_id VARCHAR(255),
  payment_status ENUM('pending', 'completed', 'failed', 'refunded'),
  processed_at
)

-- Inventory Tracking (Redis Cluster for real-time updates)
-- Key pattern: inventory:{drop_id}:{product_id}:{variant_id}
-- Value: current stock count
-- Features: Atomic decrements, expiration, pub/sub for notifications

-- Analytics Events (ClickHouse - Columnar for fast aggregation)
analytics_events (
  event_id,
  user_id,
  creator_id,
  drop_id,
  product_id,
  event_type, -- view/follow/unfollow/order/purchase
  timestamp,
  session_id,
  user_agent,
  ip_address,
  metadata JSONB -- flexible event data
)
```

### Database Scaling Strategies

#### Follow Service Sharding
- **Shard Key**: `creator_id` ensures all followers for a creator are on the same shard
- **Shard Count**: 16 shards initially, can be increased as needed
- **Query Routing**: Application-level routing based on creator_id hash
- **Cross-shard Queries**: Handled by application aggregation layer

#### Order Partitioning  
- **Partition Strategy**: Monthly partitions by `created_at`
- **Benefits**: Improved query performance, easier archival of old orders
- **Partition Pruning**: Queries automatically target relevant partitions

#### Redis Inventory Management
- **Atomic Operations**: DECR commands prevent overselling
- **Pub/Sub**: Real-time stock updates broadcast to connected clients
- **Expiration**: Auto-cleanup of ended drops
- **Persistence**: RDB snapshots + AOF for durability

####  **Strengths of the Design**

1. **Sharded Follow System**: Partitioning follows by `creator_id` brilliantly solves the celebrity creator scalability problem
2. **Hybrid Storage Strategy**: Using PostgreSQL for transactional data, Redis for inventory, and ClickHouse for analytics optimizes each use case
3. **Idempotency Handling**: Unique `idempotency_key` in orders prevents duplicate submissions
4. **Partitioned Orders**: Monthly partitioning improves query performance and enables easy archival
5. **Inventory Separation**: Redis-based inventory with PostgreSQL caching strikes the right balance between performance and consistency
6. **Analytics Foundation**: ClickHouse setup enables powerful business intelligence and performance monitoring


####  **Scalability Features**

- **Read Replicas**: Handles the 500+ RPS read requirement
- **Sharding**: Prevents celebrity creator bottlenecks (millions of followers)
- **Partitioning**: Maintains order query performance as data grows
- **Redis Cluster**: Supports 150+ order attempts/second with atomic operations

## API Design

### Public REST API

```
# User & Creator Management
GET /api/v1/users/{user_id}/profile
PUT /api/v1/users/{user_id}/profile
GET /api/v1/creators/{creator_id}
GET /api/v1/creators/{creator_id}/followers?page=1&limit=50
GET /api/v1/users/{user_id}/following?page=1&limit=50

# Follow Operations  
POST /api/v1/follows
DELETE /api/v1/follows/{creator_id}
GET /api/v1/follows/{user_id}/{creator_id}/status

# Product & Drop Browsing
GET /api/v1/products?page=1&limit=20&creator_id=&category=&active_only=true
GET /api/v1/drops?page=1&limit=20&status=live&creator_id=
GET /api/v1/drops/{drop_id}
GET /api/v1/drops/{drop_id}/items

# Order Management
POST /api/v1/orders
PUT /api/v1/orders/{order_id}
GET /api/v1/orders/{order_id}
GET /api/v1/users/{user_id}/orders?page=1&limit=20

# Real-time Stock
GET /api/v1/drops/{drop_id}/inventory
WebSocket: /ws/drops/{drop_id}/stock

# Analytics (Internal)
POST /api/v1/analytics/events
```

### Internal RPC APIs

```protobuf
// Follow Service
service FollowService {
  rpc GetFollowers(GetFollowersRequest) returns (FollowersResponse);
  rpc GetFollowCount(CreatorRequest) returns (CountResponse);
  rpc CreateFollow(FollowRequest) returns (FollowResponse);
}

// Inventory Service  
service InventoryService {
  rpc ReserveStock(ReservationRequest) returns (ReservationResponse);
  rpc ReleaseStock(ReleaseRequest) returns (ReleaseResponse);
  rpc GetCurrentStock(StockRequest) returns (StockResponse);
}

// Notification Service
service NotificationService {
  rpc SendNotification(NotificationRequest) returns (NotificationResponse);
  rpc GetUserPreferences(UserRequest) returns (PreferencesResponse);
}
```

## Caching Strategy

### Multi-Layer Caching Approach

1. **CDN Level**: Static assets, product images (TTL: 24 hours)
2. **API Gateway**: Response caching for read-heavy endpoints (TTL: 5 minutes)
3. **Redis Cache**: 
   - Product details (TTL: 15 minutes)
   - Creator profiles (TTL: 1 hour)
   - Follower counts (TTL: 5 minutes)
   - Search results (TTL: 10 minutes)
     (TTL are just estimate numbers and could be changed if needed)

### Cache Invalidation Strategy
- **Write-through**: Critical data (inventory, orders) bypass cache
- **Event-based invalidation**: Kafka events trigger cache updates
- **Time-based expiry**: Appropriate TTL values for different data types
- **Manual invalidation**: Admin tools for immediate cache clearing

## Handling High Concurrency & Scale

### Inventory Management
- **Distributed Locking**: Redis-based locks prevent overselling
- **Optimistic Concurrency Control**: Version-based updates with retry logic
- **Event Sourcing**: Immutable inventory transaction log

### Follower Scalability
- **Sharded Follow Service**: Partition followers by creator ID
- **Read Replicas**: Separate read/write databases for follower queries
- **Materialized Views**: Pre-computed follower counts and lists

### Order Idempotency
- **Unique Keys**: Client-generated idempotency keys prevent duplicates
- **Deduplication Window**: A certain time window for retry protection

## Real-time Notifications

### Notification Delivery Pipeline
1. **Event Generation**: Services publish events to Kafka topics
2. **Notification Service**: Consumes events and determines recipients
3. **Delivery Mechanisms**: 
   - WebSocket for active users
   - Push notifications for mobile apps
   - Email for critical updates

### Notification Types
- Drop start notifications
- Low stock alerts (configurable threshold)
- Sold out notifications
- Order confirmations

## Performance Optimizations

### Database Optimizations
- **Indexing Strategy**: Composite indexes on frequently queried columns
- **Query Optimization**: N+1 prevention, efficient pagination
- **Connection Pooling**: Managed database connections

### Service-Level Optimizations
- **Horizontal Scaling**: Auto-scaling based on CPU/memory metrics
- **Circuit Breakers**: Prevent cascade failures
- **Rate Limiting**: Protect against abuse and ensure fair usage

## Security Considerations

- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **API Security**: Request signing, rate limiting, input validation
- **Data Privacy**: PII encryption, secure data transmission (TLS)
- **Inter-service Security**: mTLS for service-to-service communication

## Monitoring & Observability

### Key Metrics
- Request latency (p95, p99)
- Cache hit ratios
- Order processing throughput
- Inventory lock contention
- Notification delivery rates

### Monitoring Stack
- **Application Metrics**: Custom business metrics
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Distributed Tracing**: Request flow across services
- **Log Aggregation**: Centralized logging with correlation IDs

## Trade-offs & Design Decisions

### Consistency vs Availability
- **Eventual Consistency**: Follower counts for better performance
- **Strong Consistency**: Inventory and orders to prevent overselling
- **Read Replicas**: Accept slight read delay for improved scalability

### Microservices vs Monolith
- **Pros**: Independent scaling, technology diversity, fault isolation
- **Cons**: Network overhead, distributed system complexity
- **Justification**: Requirements demand independent scaling of different components

### Caching Strategy
- **Aggressive Caching**: Improves read performance but increases complexity
- **Cache Invalidation**: Trade-off between freshness and performance
- **Memory Usage**: Redis memory costs vs database load reduction

### Event-Driven Architecture
- **Asynchronous Processing**: Better scalability but eventual consistency
- **Message Queue Overhead**: Additional infrastructure complexity
- **Replay Capability**: Event sourcing enables debugging and analytics

- **Advanced Analytics**: Real-time drop performance metrics
- **Mobile Optimization**: Offline capability and push notification improvements
