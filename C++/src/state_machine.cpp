#include "state_machine.hpp"
#include <rapidfuzz/fuzz.hpp>
#include <iostream>
#include <algorithm>
#include <curl/curl.h>
#include <sstream>

std::map<std::string, std::map<std::string, std::string>> StateMachine::all_keywords;

// Hàm helper cho Bot nói (giữ nguyên)
void bot_speak(std::string msg, StateMachine* sm) {
    std::cout << ">>> Bot: " << msg << std::endl;
    sm->send_websocket_message({{"type", "assistantSpeak"}, {"text", msg}});

    CURL *curl = curl_easy_init();
    if (curl) {
        char* encoded = curl_easy_escape(curl, msg.c_str(), msg.length());
        std::string url = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q=" + std::string(encoded);
        curl_free(encoded);
        FILE *fp = fopen("speech.mp3", "wb");
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);
        curl_easy_setopt(curl, CURLOPT_USERAGENT, "Mozilla/5.0");
        if (curl_easy_perform(curl) == CURLE_OK) {
            fclose(fp);
            system("mpg123 -q speech.mp3 &");
        } else { fclose(fp); }
        curl_easy_cleanup(curl);
    }
}

StateMachine::StateMachine() {
    webSocket.setOnMessageCallback([](const ix::WebSocketMessagePtr& msg){});
    trigger_keywords = {"hey abm", "hey you", "abm", "hey a b m", "apm", "ibm", "ipm"};
    all_keywords["Size"] = {{"S","small"}, {"M","medium"}, {"L","large"}};
    all_keywords["YesNo"] = {{"Yes","yes"}, {"No","no"}};
    
    webSocket.setUrl("ws://localhost:8085/voice"); 
    webSocket.start();
    reset(); 
}

// FIX: Đảm bảo có StateMachine:: ở tất cả các hàm thành viên
void StateMachine::parse_ingredients(std::string drink_name, std::string raw_ing) {
    std::string clean = raw_ing;
    clean.erase(std::remove(clean.begin(), clean.end(), '{'), clean.end());
    clean.erase(std::remove(clean.begin(), clean.end(), '}'), clean.end());
    std::vector<std::string> components;
    std::stringstream ss(clean);
    std::string item;
    while (std::getline(ss, item, ',')) {
        item.erase(0, item.find_first_not_of(" "));
        item.erase(item.find_last_not_of(" ") + 1);
        if(!item.empty()) components.push_back(item);
    }
    drink_components[drink_name] = components;
}

void StateMachine::set_drinks(const std::vector<std::string>& drinks) {
    all_keywords["Drink"].clear();
    for (const auto& d : drinks) {
        std::string low = d;
        std::transform(low.begin(), low.end(), low.begin(), ::tolower);
        all_keywords["Drink"][d] = low; // Label là d, Keyword so sánh là low
        std::cout << "[DEBUG] Loaded Drink keyword: '" << low << "'" << std::endl;
    }
}

void StateMachine::send_websocket_message(const nlohmann::json& j) {
    if (webSocket.getReadyState() == ix::ReadyState::Open) {
        webSocket.send(j.dump());
    }
}

void StateMachine::reset() {
    current_step = OrderStep::WAITING_FOR_TRIGGER;
    waiting_confirmation = false;
    current_comp_idx = 0;
    current_order = {};
    pending_value = "";
    pending_category = "";
}

std::string StateMachine::detect_best_match(const std::string& text, const std::string& category) {
    if (all_keywords[category].empty()) {
        std::cout << "[DEBUG] Category " << category << " is EMPTY!" << std::endl;
        return "";
    }
    
    std::string best = ""; double max_s = 0;
    for (auto const& [label, kw] : all_keywords[category]) {
        double s = rapidfuzz::fuzz::partial_ratio(text, kw);
        if (s > max_s) { max_s = s; best = label; }
    }
    
    std::cout << "[DEBUG] Category: " << category << " | Input: " << text 
              << " | Best Match: " << best << " (" << max_s << "%)" << std::endl;
              
    return (max_s >= 60.0) ? best : ""; 
}

void StateMachine::process_text(const std::string& raw_text) {
    std::string text = raw_text;
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    
    // Gửi text người dùng nói lên WebSocket để hiển thị Overlay
    send_websocket_message({{"type", "userSpeak"}, {"text", text}}); 

    if (current_step == OrderStep::WAITING_FOR_TRIGGER) {
        for (const auto& kw : trigger_keywords) {
            if (text.find(kw) != std::string::npos) {
                send_websocket_message({{"type", "start"}});
                bot_speak("Yes, I'm here. What would you like to drink?", this);
                current_step = OrderStep::DRINK_SELECTION;
                return;
            }
        }
    }

    if (waiting_confirmation) {
        std::string ans = detect_best_match(text, "YesNo");
        if (ans == "Yes") {
            if (pending_category == "Drink") {
                current_order.drink_name = pending_value;
                if (drink_components.count(current_order.drink_name) && !drink_components[current_order.drink_name].empty()) {
                    bot_speak("You choose " + pending_value + ". Would you like to customize the ingredients?", this);
                    current_step = OrderStep::CUSTOMIZE_CHOICE;
                    pending_category = "CustomizeConfirm";
                } else {
                    bot_speak("You choose " + pending_value + ". What size would you like?", this);
                    current_step = OrderStep::SIZE_SELECTION;
                    waiting_confirmation = false;
                }
            } 
            else if (pending_category == "CustomizeConfirm") {
                current_comp_idx = 0;
                current_drink_comps = drink_components[current_order.drink_name];
                bot_speak("What size for " + current_drink_comps[current_comp_idx] + "?", this);
                current_step = OrderStep::COMPONENT_CUSTOM;
                waiting_confirmation = false; 
            }
            else if (pending_category == "Final") {
                // Đóng gói JSON gửi về frontend Laravel
                nlohmann::json res;
                res["type"] = "voiceOrderResult"; 
                res["data"]["drink"] = current_order.drink_name;
                res["data"]["details"]["Price"] = drink_prices[current_order.drink_name];
                
                if (current_order.ingredients.empty()) {
                    for (auto& c : drink_components[current_order.drink_name])
                        res["data"]["details"][c] = current_order.global_size;
                } else {
                    for (auto const& [ing, sz] : current_order.ingredients)
                        res["data"]["details"][ing] = sz;
                }
                send_websocket_message(res); 
                bot_speak("Order successful! Enjoy your " + current_order.drink_name + ".", this);
                reset();
            }
            return;
        } else if (ans == "No") {
            bot_speak("Sorry, what drink do you want?", this);
            current_step = OrderStep::DRINK_SELECTION;
            waiting_confirmation = false;
            return;
        }
    }

    if (current_step == OrderStep::DRINK_SELECTION) {
        std::string d = detect_best_match(text, "Drink");
        if (!d.empty()) { 
            pending_value = d; pending_category = "Drink"; 
            bot_speak("You said " + d + ", did you mean a drink " + d + "?", this); 
            waiting_confirmation = true; 
        }
    } else if (current_step == OrderStep::SIZE_SELECTION) {
        std::string s = detect_best_match(text, "Size");
        if (!s.empty()) { 
            current_order.global_size = s; 
            bot_speak("Confirm: " + current_order.drink_name + " - size " + s + ". Correct?", this); 
            pending_category = "Final"; waiting_confirmation = true; 
        }
    } else if (current_step == OrderStep::COMPONENT_CUSTOM) {
        std::string s = detect_best_match(text, "Size");
        if (!s.empty()) {
            current_order.ingredients[current_drink_comps[current_comp_idx]] = s;
            current_comp_idx++;
            if (current_comp_idx < (int)current_drink_comps.size()) 
                bot_speak("What size for " + current_drink_comps[current_comp_idx] + "?", this);
            else { 
                bot_speak("Everything looks correct. Is this right?", this); 
                pending_category = "Final"; waiting_confirmation = true; 
            }
        }
    }
}