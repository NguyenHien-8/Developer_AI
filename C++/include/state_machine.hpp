#ifndef STATE_MACHINE_HPP
#define STATE_MACHINE_HPP

#include <string>
#include <vector>
#include <map>
#include <ixwebsocket/IXWebSocket.h>
#include <nlohmann/json.hpp>

enum class OrderStep { 
    WAITING_FOR_TRIGGER, 
    DRINK_SELECTION, 
    CUSTOMIZE_CHOICE, 
    SIZE_SELECTION, 
    COMPONENT_CUSTOM, 
    FINAL_CONFIRMATION 
};

struct Order {
    std::string drink_name;
    std::string global_size;
    std::map<std::string, std::string> ingredients;
};

class StateMachine {
public:
    StateMachine();
    void process_text(const std::string& text);
    void reset();
    void set_drinks(const std::vector<std::string>& drinks);
    void parse_ingredients(std::string drink_name, std::string raw_ing);
    void send_websocket_message(const nlohmann::json& message);

    static std::map<std::string, std::map<std::string, std::string>> all_keywords;
    std::vector<std::string> trigger_keywords;
    std::map<std::string, std::vector<std::string>> drink_components;
    std::map<std::string, int> drink_prices;

private:
    OrderStep current_step;
    Order current_order;
    bool waiting_confirmation;
    std::string pending_value;
    std::string pending_category;
    int current_comp_idx;
    std::vector<std::string> current_drink_comps;
    ix::WebSocket webSocket;

    std::string detect_best_match(const std::string& text, const std::string& category);
};

#endif