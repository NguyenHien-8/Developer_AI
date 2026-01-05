#ifndef API_HANDLER_HPP
#define API_HANDLER_HPP

#include <curl/curl.h>
#include <string>
#include <iostream>

class ApiHandler {
public:
    static void sendResult(std::string age_group, float gender_avg) {
        CURL* curl = curl_easy_init();
        if (curl) {
            // URL server của bạn
            std::string url = "http://127.0.0.1:8000/analyze_result"; 
            
            // Format JSON giống hệt kết quả trả về trong main.py
            std::string jsonData = "{\"age\": \"" + age_group + "\", \"gender\": " + std::to_string(gender_avg) + "}";

            struct curl_slist *headers = NULL;
            headers = curl_slist_append(headers, "Content-Type: application/json");

            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonData.c_str());
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

            CURLcode res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                std::cerr << "API Error: " << curl_easy_strerror(res) << std::endl;
            }

            curl_easy_cleanup(curl);
            curl_slist_free_all(headers);
        }
    }
};

#endif