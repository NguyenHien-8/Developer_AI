#ifndef DATABASE_HPP
#define DATABASE_HPP

#include <string>
#include <vector>
#include <map>
#include <nlohmann/json.hpp>

// Cấu trúc dữ liệu đồ uống tương đương với dữ liệu từ Supabase của bạn
struct DrinkInfo {
    std::string name;
    int price;
    std::vector<std::string> ingredients;
};

class Database {
public:
    Database(const std::string& url, const std::string& key);
    
    // Hàm lấy toàn bộ dữ liệu đồ uống (thay cho fetch_drinks_from_supabase)
    std::vector<DrinkInfo> fetch_all_drinks();

private:
    std::string supabase_url;
    std::string supabase_key;
    
    // Hàm bổ trợ để thực hiện HTTP GET
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp);
    std::string perform_get_request(const std::string& table);
};

#endif