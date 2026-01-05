#include <vector>
#include <map>
#include <numeric>

class Analyzer {
public:
    // Tìm nhóm tuổi phổ biến nhất bằng cách chia cho 10 [cite: 95]
    static int getMostCommonAgeGroup(const std::vector<int>& ages) {
        std::map<int, int> counts;
        for (int a : ages) counts[a / 10]++; [cite: 95]
        // Tìm Max...
        return most_common;
    }

    // Logic hiệu chỉnh giới tính đặc biệt (nếu gender < 0.5 nhưng có high confidence) [cite: 66]
    static float calculateFinalGender(const std::vector<float>& genders, int highConfCount) {
        float avg = std::accumulate(genders.begin(), genders.end(), 0.0f) / genders.size();
        if (avg < 0.5 && highConfCount >= 3) return 1.2f; // Quy ước Female chắc chắn [cite: 66]
        return avg;
    }
};