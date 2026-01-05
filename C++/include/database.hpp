#ifndef DATABASE_HPP
#define DATABASE_HPP

#include <string>
#include <vector>

struct DrinkInfo {
    std::string drink_name; // Phải là drink_name, không phải name
    std::string ingredients; // Phải là ingredients, không phải ingredients_raw
    int price;
    // ... các trường khác ...
};

class Database {
public:
    Database(std::string url, std::string key);
    std::vector<DrinkInfo> fetch_all_drinks();

private:
    std::string api_url;
    std::string api_key;
    std::string perform_curl_request(); 
};

#endif