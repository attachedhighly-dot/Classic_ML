impl OrderBook {
    pub fn limit_order(&mut self, mut taker_order: Order, side: OrderSide) -> Vec<Trade> {
        let mut trades = Vec::new();

        match side {
            OrderSide::Buy => {
                // Loop through asks (sells) starting from the lowest price
                while taker_order.quantity > 0 {
                    if let Some(mut entry) = self.asks.first_entry() {
                        let &ask_price = entry.key();
                        
                        // Condition check: Taker buy price must be >= Maker sell price
                        if taker_order.price < ask_price {
                            break; 
                        }

                        let queue = entry.get_mut();
                        while taker_order.quantity > 0 && !queue.is_empty() {
                            let mut maker_order = queue.pop_front().unwrap();
                            let match_quantity = std::cmp::min(taker_order.quantity, maker_order.quantity);

                            trades.push(Trade {
                                maker_order_id: maker_order.id,
                                taker_order_id: taker_order.id,
                                price: ask_price, // Executed at the maker's price
                                quantity: match_quantity,
                            });

                            taker_order.quantity -= match_quantity;
                            maker_order.quantity -= match_quantity;

                            // If maker order still has remaining volume, put it back at the front
                            if maker_order.quantity > 0 {
                                queue.push_front(maker_order);
                            }
                        }

                        // Clean up empty price levels
                        if queue.is_empty() {
                            entry.remove();
                        }
                    } else {
                        break; // No more asks available
                    }
                }

                // If taker order is not fully filled, rest the remainder on the bid book
                if taker_order.quantity > 0 {
                    self.bids
                        .entry(std::cmp::Reverse(taker_order.price))
                        .or_insert_with(VecDeque::new)
                        .push_back(taker_order);
                }
            }

            OrderSide::Sell => {
                // Loop through bids (buys) starting from the highest price
                while taker_order.quantity > 0 {
                    if let Some(mut entry) = self.bids.first_entry() {
                        let bid_price = entry.key().0;

                        // Condition check: Taker sell price must be <= Maker buy price
                        if taker_order.price > bid_price {
                            break;
                        }

                        let queue = entry.get_mut();
                        while taker_order.quantity > 0 && !queue.is_empty() {
                            let mut maker_order = queue.pop_front().unwrap();
                            let match_quantity = std::cmp::min(taker_order.quantity, maker_order.quantity);

                            trades.push(Trade {
                                maker_order_id: maker_order.id,
                                taker_order_id: taker_order.id,
                                price: bid_price,
                                quantity: match_quantity,
                            });

                            taker_order.quantity -= match_quantity;
                            maker_order.quantity -= match_quantity;

                            if maker_order.quantity > 0 {
                                queue.push_front(maker_order);
                            }
                        }

                        if queue.is_empty() {
                            entry.remove();
                        }
                    } else {
                        break; // No more bids available
                    }
                }

                // If taker order is not fully filled, rest the remainder on the ask book
                if taker_order.quantity > 0 {
                    self.asks
                        .entry(taker_order.price)
                        .or_insert_with(VecDeque::new)
                        .push_back(taker_order);
                }
            }
        }

        trades
    }
}
