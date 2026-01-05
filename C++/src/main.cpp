#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <numeric>
#include <map>
#include <ixwebsocket/IXWebSocket.h>
#include <nlohmann/json.hpp>

using namespace cv;
using namespace std;
using json = nlohmann::json;

// Quản lý trạng thái và đồng bộ luồng
mutex frameLock;
Mat globalFrame;
bool isRunning = true;
bool startAnalysis = false; 

// Thay thế Processor.hpp bằng logic trực tiếp
Rect getPaddedRect(Rect r, int width, int height) {
    int padding = r.height * 0.2;
    int x = max(0, r.x);
    int y = max(0, r.y - padding);
    int w = min(width - x, r.width);
    int h = min(height - y, r.height + padding);
    return Rect(x, y, w, h);
}

string findMostCommonAgeGroup(const vector<int>& ages) {
    if (ages.empty()) return "20s";
    map<int, int> counts;
    for (int age : ages) counts[age / 10]++;
    int mostCommon = 2, maxCount = 0;
    for (auto const& [group, count] : counts) {
        if (count > maxCount) { maxCount = count; mostCommon = group; }
    }
    return to_string(mostCommon * 10) + "s";
}

// Luồng xử lý AI
void aiProcessingLoop(dnn::Net& ageNet, dnn::Net& genderNet, CascadeClassifier& faceCascade, ix::WebSocket& webSocket) {
    const int PROCESS_NUM = 20; 
    vector<float> genderBatch;
    vector<int> ageBatch;
    int highConfCount = 0;

    while (isRunning) {
        if (!startAnalysis) {
            this_thread::sleep_for(chrono::milliseconds(100));
            continue;
        }

        Mat frame;
        {
            lock_guard<mutex> lock(frameLock);
            if (!globalFrame.empty()) frame = globalFrame.clone();
        }

        if (frame.empty()) continue;

        Mat gray;
        vector<Rect> faces;
        cvtColor(frame, gray, COLOR_BGR2GRAY);
        faceCascade.detectMultiScale(gray, faces, 1.1, 7, 0, Size(30, 30));

        for (const auto& r : faces) {
            Rect paddedBox = getPaddedRect(r, frame.cols, frame.rows);
            Mat faceImg = frame(paddedBox).clone();
            Mat blob = dnn::blobFromImage(faceImg, 1.0, Size(227, 227), Scalar(78.42, 87.76, 114.16));

            genderNet.setInput(blob);
            float genderScore = genderNet.forward().at<float>(0, 1);

            ageNet.setInput(blob);
            Mat aPreds = ageNet.forward();
            double maxV; Point maxL;
            minMaxLoc(aPreds, NULL, &maxV, NULL, &maxL);
            int ageVal = maxL.x * 10;

            if (genderScore < 0.3) ageVal += 5;
            if (genderScore > 0.98) highConfCount++;

            genderBatch.push_back(genderScore);
            ageBatch.push_back(ageVal);

            if (genderBatch.size() >= PROCESS_NUM) {
                float avgGender = accumulate(genderBatch.begin(), genderBatch.end(), 0.0f) / PROCESS_NUM;
                if (avgGender < 0.5 && highConfCount >= 3) avgGender = 1.2f;

                string ageGroupStr = findMostCommonAgeGroup(ageBatch);
                int ageInt = stoi(ageGroupStr.substr(0, 2)) / 10; 

                // Gửi JSON khớp với cameraUtils.js
                json response;
                response["type"] = "recommend_result";
                response["data"]["status"] = "ok"; //
                response["data"]["type"] = "unknown_customer"; //
                response["data"]["gender"] = (avgGender > 0.5 ? 1.0f : 0.0f); //
                response["data"]["age"] = ageInt; //

                webSocket.send(response.dump());
                cout << ">>> Client Sent Result: " << response.dump() << endl;

                genderBatch.clear(); ageBatch.clear(); highConfCount = 0;
                startAnalysis = false; 
            }
            break; 
        }
        this_thread::sleep_for(chrono::milliseconds(30));
    }
}

int main() {
    ix::WebSocket webSocket;
    string url = "ws://localhost:8085/face";
    webSocket.setUrl(url);

    webSocket.setOnMessageCallback([&](const ix::WebSocketMessagePtr& msg) {
        if (msg->type == ix::WebSocketMessageType::Message) {
            try {
                auto j = json::parse(msg->str);
                if (j["type"] == "recommend") {
                    cout << "Request received from JS Server: Start Analysis..." << endl;
                    startAnalysis = true;
                }
            } catch (...) {}
        } else if (msg->type == ix::WebSocketMessageType::Open) {
            cout << "Connected to JS Server at " << url << endl;
        } else if (msg->type == ix::WebSocketMessageType::Error) {
            cerr << "Connection Error: " << msg->errorInfo.reason << endl;
        }
    });

    webSocket.start();

    CascadeClassifier faceCascade("assets/haarcascade_frontalface_alt.xml");
    dnn::Net ageNet = dnn::readNetFromCaffe("models/deploy_age2.prototxt", "models/age_net.caffemodel");
    dnn::Net genderNet = dnn::readNetFromCaffe("models/deploy_gender2.prototxt", "models/gender_net.caffemodel");

    thread cameraThread([&]() {
        VideoCapture cap(0);
        Mat frame;
        while (isRunning) {
            cap >> frame;
            if (frame.empty()) continue;
            flip(frame, frame, 1);
            {
                lock_guard<mutex> lock(frameLock);
                globalFrame = frame.clone();
            }
            this_thread::sleep_for(chrono::milliseconds(10));
        }
    });

    thread aiThread(aiProcessingLoop, ref(ageNet), ref(genderNet), ref(faceCascade), ref(webSocket));

    // Giữ chương trình chạy
    while (isRunning) {
        this_thread::sleep_for(chrono::seconds(1));
    }

    webSocket.stop();
    cameraThread.join();
    aiThread.join();
    return 0;
}