#include "database.hpp"
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <iostream>

size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

Database::Database(std::string url, std::string key) : api_url(url), api_key(key) {}

std::string Database::perform_curl_request() {
    CURL* curl;
    CURLcode res;
    std::string readBuffer;
    curl = curl_easy_init();
    if(curl) {
        // Gọi bảng drinkdata
        std::string url = api_url + "/rest/v1/drinkdata?select=*";
        struct curl_slist* headers = NULL;
        headers = curl_slist_append(headers, ("apikey: " + api_key).c_str());
        headers = curl_slist_append(headers, ("Authorization: Bearer " + api_key).c_str());

        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
        res = curl_easy_perform(curl);
        curl_easy_cleanup(curl);
        curl_slist_free_all(headers);
    }
    return readBuffer;
}

std::vector<DrinkInfo> Database::fetch_all_drinks() {
    std::vector<DrinkInfo> drinks;
    std::string resp = perform_curl_request();
    try {
        auto j = nlohmann::json::parse(resp);
        for (auto& item : j) {
            DrinkInfo d;
            // Khớp với cột 'name' trong DB của bạn
            d.drink_name = item.value("name", "");
            d.price = item.value("price", 0);
            drinks.push_back(d);
        }
    } catch (...) {}
    return drinks;
}