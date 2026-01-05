#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <portaudio.h>
#include <nlohmann/json.hpp>
#include "vosk_api.h"
#include "state_machine.hpp"
#include "database.hpp"

#define SAMPLE_RATE 16000
#define FRAMES_PER_BUFFER 4000

std::queue<std::vector<short>> audio_queue;
std::mutex queue_mutex;

static int paCallback(const void *inputBuffer, void *outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo *timeInfo, PaStreamCallbackFlags statusFlags, void *userData)
{
    const short *data = (const short *)inputBuffer;
    if (data)
    {
        std::lock_guard<std::mutex> lock(queue_mutex);
        audio_queue.push(std::vector<short>(data, data + framesPerBuffer));
    }
    return paContinue;
}

int main()
{
    Database db("https://safsghcjddrtiyqpyxqe.supabase.co", 
                "sb_publishable_eva0YZlUxTBebrRfvculnw_SwLgz9Pr"); 
    
    auto drinks_db = db.fetch_all_drinks();
    StateMachine sm;
    
    std::cout << "\n--- SYNCING DATA FROM SUPABASE ---" << std::endl;
    
    std::vector<std::string> names;
    for (const auto& d : drinks_db) {
        // In ra để debug xem dữ liệu có thực sự được nạp vào struct không
        std::cout << "[DB DEBUG] Fetching Name: '" << d.drink_name << "' | Ings: '" << d.ingredients << "'" << std::endl;
        
        if (!d.drink_name.empty()) {
            names.push_back(d.drink_name);
            sm.parse_ingredients(d.drink_name, d.ingredients); 
            sm.drink_prices[d.drink_name] = (int)d.price;
        }
    }

    if (names.empty()) {
        std::cout << "[ERROR] No valid drink names found! Using backup coffee." << std::endl;
        names.push_back("coffee");
        sm.parse_ingredients("coffee", "{Coffee,Sugar}");
        sm.drink_prices["coffee"] = 12;
    }

    sm.set_drinks(names); 
    std::cout << "Successfully synced " << names.size() << " drinks." << std::endl;

    // Khởi tạo Vosk ...
    VoskModel *model = vosk_model_new("/home/huang/Documents/ABM/Voice_C++/models/vosk-model-small-en-us-0.15");
    VoskRecognizer *recognizer = vosk_recognizer_new(model, 16000);

    // Khởi tạo PortAudio ...
    Pa_Initialize();
    PaStream *stream;
    Pa_OpenDefaultStream(&stream, 1, 0, paInt16, 16000, 4000, paCallback, NULL);
    Pa_StartStream(stream);

    std::cout << "\n--- AUTO BARISTA READY ---" << std::endl;

    while (true)
    {
        std::vector<short> buffer;
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            if (!audio_queue.empty())
            {
                buffer = audio_queue.front();
                audio_queue.pop();
            }
        }
        if (!buffer.empty())
        {
            if (vosk_recognizer_accept_waveform_s(recognizer, buffer.data(), buffer.size()))
            {
                nlohmann::json j = nlohmann::json::parse(vosk_recognizer_result(recognizer));
                std::string text = j.value("text", "");
                if (!text.empty())
                {
                    std::cout << "\n[USER]: " << text << std::endl;
                    sm.process_text(text);
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}