#include <iostream>
#include <map>
#include <unordered_map>
#include <list>
#include <vector>
#include <string>
#include <memory>
#include <chrono>


//• Time Priority: Orders are filled first by best price, and then by the earliest arrival time at that price level for displayed limit orders.
• Ultra-Low Latency: Production matching architectures operate at microsecond speeds—frequently sub-40 microseconds down to around 14 microseconds door-to-door.
• Standard Industry Protocols:
	• FIX (Financial Information eXchange): For order routing and management.
	• OUCH / ITCH: Low-latency protocols for fast order entry (OUCH) and real-time market data/order book feeds (ITCH).
	• SoupBinTCP / MoldUDP64: Transport-level framing for reliable or multicast stream delivery.
• Multi-Asset & Scalable: Designed to handle equities, options, fixed income, foreign exchange, crypto, and fractionalized assets with horizontal scalability.


// Simplified Nasdaq Order Book Types
enum class Side { BUY, SELL };

struct Order {
    uint64_t order_id;
    std::string symbol;
    Side side;
    uint32_t price;     // Prices scaled to integers (e.g., $100.50 -> 10050)
    uint32_t qty;       // Remaining quantity
    uint64_t timestamp; // Time-priority key
};

// Represents a unique price level in the order book
struct PriceLevel {
    uint32_t price;
    std::list<std::shared_ptr<Order>> orders; // FIFO queue for time priority
    uint32_t total_qty = 0;
};

class NasdaqEngine {
private:
    // Buy book sorted descending (highest bid first); Sell book sorted ascending (lowest ask first)
    std::map<uint32_t, PriceLevel, std::greater<uint32_t>> bids;
    std::map<uint32_t, PriceLevel, std::less<uint32_t>> asks;
    
    // Quick lookup for order cancellation or tracking
    std::unordered_map<uint64_t, std::list<std::shared_ptr<Order>>::iterator> order_map;
    std::unordered_map<uint64_t, uint32_t> order_price_map; // Maps order_id to its price level

    uint64_t get_timestamp() {
        return std::chrono::duration_cast<std::chrono::nanoseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch()).count();
    }

    // Simulates an ITCH (Market Data) Execution Message
    void broadcast_trade(uint64_t match_id, uint32_t price, uint32_t qty) {
        std::cout << "[ITCH MARKET DATA] TRADE EXECUTION -> Match ID: " << match_id 
                  << " | Price: " << (price / 100.0) << " | Qty: " << qty << "\n";
    }

public:
    // Process an incoming limit order (Simulates OUCH Inbound Order)
    void submit_order(uint64_t order_id, const std::string& symbol, Side side, uint32_t price, uint32_t qty) {
        auto order = std::make_shared<Order>(Order{order_id, symbol, side, price, qty, get_timestamp()});
        
        if (side == Side::BUY) {
            // Attempt to match with existing resting Asks
            while (order->qty > 0 && !asks.empty() && asks.begin()->first <= order->price) {
                auto& lowest_ask_level = asks.begin()->second;
                auto it = lowest_ask_level.orders.begin();
                
                while (it != lowest_ask_level.orders.end() && order->qty > 0) {
                    auto resting_order = *it;
                    uint32_t match_qty = std::min(order->qty, resting_order->qty);
                    
                    // Execute match
                    order->qty -= match_qty;
                    resting_order->qty -= match_qty;
                    lowest_ask_level.total_qty -= match_qty;
                    
                    broadcast_trade(order->timestamp, lowest_ask_level.price, match_qty);
                    
                    if (resting_order->qty == 0) {
                        order_map.erase(resting_order->order_id);
                        order_price_map.erase(resting_order->order_id);
                        it = lowest_ask_level.orders.erase(it);
                    } else {
                        ++it;
                    }
                }
                if (lowest_ask_level.orders.empty()) {
                    asks.erase(asks.begin());
                }
            }
            // If remaining quantity exists, add to resting Bids (Price-Time Priority)
            if (order->qty > 0) {
                auto& level = bids[order->price];
                level.price = order->price;
                level.orders.push_back(order);
                level.total_qty += order->qty;
                order_map[order_id] = std::prev(level.orders.end());
                order_price_map[order_id] = order->price;
            }
        } 
        else { // Side::SELL
            // Attempt to match with existing resting Bids
            while (order->qty > 0 && !bids.empty() && bids.begin()->first >= order->price) {
                auto& highest_bid_level = bids.begin()->second;
                auto it = highest_bid_level.orders.begin();
                
                while (it != highest_bid_level.orders.end() && order->qty > 0) {
                    auto resting_order = *it;
                    uint32_t match_qty = std::min(order->qty, resting_order->qty);
                    
                    order->qty -= match_qty;
                    resting_order->qty -= match_qty;
                    highest_bid_level.total_qty -= match_qty;
                    
                    broadcast_trade(order->timestamp, highest_bid_level.price, match_qty);
                    
                    if (resting_order->qty == 0) {
                        order_map.erase(resting_order->order_id);
                        order_price_map.erase(resting_order->order_id);
                        it = highest_bid_level.orders.erase(it);
                    } else {
                        ++it;
                    }
                }
                if (highest_bid_level.orders.empty()) {
                    bids.erase(bids.begin());
                }
            }
            // If remaining quantity exists, add to resting Asks
            if (order->qty > 0) {
                auto& level = asks[order->price];
                level.price = order->price;
                level.orders.push_back(order);
                level.total_qty += order->qty;
                order_map[order_id] = std::prev(level.orders.end());
                order_price_map[order_id] = order->price;
            }
        }
    }

    // Cancel order function (Simulates OUCH Cancel)
    void cancel_order(uint64_t order_id) {
        auto map_it = order_map.find(order_id);
        if (map_it == order_map.end()) return;

        uint32_t price = order_price_map[order_id];
        auto order_list_it = map_it->second;
        auto order = *order_list_it;

        if (order->side == Side::BUY) {
            bids[price].total_qty -= order->qty;
            bids[price].orders.erase(order_list_it);
            if (bids[price].orders.empty()) bids.erase(price);
        } else {
            asks[price].total_qty -= order->qty;
            asks[price].orders.erase(order_list_it);
            if (asks[price].orders.empty()) asks.erase(price);
        }

        order_map.erase(order_id);
        order_price_map.erase(order_id);
        std::cout << "[OUCH ACK] Canceled Order ID: " << order_id << "\n";
    }

    // Render Order Book Snapshot
    void print_book() {
        std::cout << "\n--- CURRENT ORDER BOOK ---" << std::endl;
        std::cout << "  [ASKS]" << std::endl;
        for (auto it = asks.rbegin(); it != asks.rend(); ++it) {
            std::cout << "    Price: $" << (it->first / 100.0) << " | Qty: " << it->second.total_qty << "\n";
        }
        std::cout << "  -------------------------" << std::endl;
        std::cout << "  [BIDS]" << std::endl;
        for (const auto& [price, level] : bids) {
            std::cout << "    Price: $" << (price / 100.0) << " | Qty: " << level.total_qty << "\n";
        }
        std::cout << "--------------------------\n" << std::endl;
    }
};

int main() {
    NasdaqEngine engine;

    std::cout << "Submitting resting liquidity..." << std::endl;
    engine.submit_order(101, "AAPL", Side::BUY, 15000, 100); // Bid $150.00
    engine.submit_order(102, "AAPL", Side::BUY, 15000, 50);  // Bid $150.00 (behind ID 101)
    engine.submit_order(103, "AAPL", Side::SELL, 15100, 80); // Ask $151.00
    engine.print_book();

    std::cout << "Submitting an aggressive sell order (Crossing the book)..." << std::endl;
    // Aggressive sell at $150.00 for 120 shares will eat all of ID 101, and 20 shares of ID 102
    engine.submit_order(104, "AAPL", Side::SELL, 15000, 120);
    
    engine.print_book();

    std::cout << "Canceling the remaining quantity of order 102..." << std::endl;
    engine.cancel_order(102);
    engine.print_book();

    return 0;
}
