use std::collections::BTreeMap;
use std::collections::VecDeque;
//ORDER BOOK
#[derive(Debug, Clone, PartialEq)]
pub enum OrderSide {
    Buy,
    Sell,
}

#[derive(Debug, Clone)]
pub struct Order {
    pub id: u64,
    pub user_id: u64,
    pub price: u64,     // Scaled integer (e.g., $100.50 represented as 10050)
    pub quantity: u64,  // Scaled integer to prevent floating-point precision issues
}

#[derive(Debug, Clone)]
pub struct Trade {
    pub maker_order_id: u64,
    pub taker_order_id: u64,
    pub price: u64,
    pub quantity: u64,
}

pub struct OrderBook {
    // Buy orders: Key is Price (inverted to sort Max to Min), Value is a queue of Orders at that price
    pub bids: BTreeMap<std::cmp::Reverse<u64>, VecDeque<Order>>,
    // Sell orders: Key is Price (sorted Min to Max), Value is a queue of Orders at that price
    pub asks: BTreeMap<u64, VecDeque<Order>>,
}

impl OrderBook {
    pub fn new() -> Self {
        Self {
            bids: BTreeMap::new(),
            asks: BTreeMap::new(),
        }
    }
}
