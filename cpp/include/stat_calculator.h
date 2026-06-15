#pragma once

#include "player.h"
#include <vector>
#include <random>

class StatCalculator {
public:
    StatCalculator();
    StatCalculator(unsigned int seed);

    int calculate_rating(const Player& player);
    int calculate_value(const Player& player, int market_state);
    int calculate_form(const std::vector<int>& recent_results, int window = 5);
    int calculate_fatigue(int matches_played, int rest_days, bool was_substituted = false);
    int calculate_morale(const std::vector<int>& results, int playing_time, int overall_rating);
    void age_regression(Player& player, int weeks);
    void progress_young_player(Player& player, int weeks);

private:
    std::mt19937 rng;

    double get_position_weight(const Player& player, const std::string& stat);
    int clamp_stat(int value);
    double get_age_factor(int age);
    double get_potential_factor(int age, int potential, int current);
    int estimate_market_modifier(int avg_reputation);
};
