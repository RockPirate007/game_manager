#pragma once

#include "player.h"
#include "team.h"
#include <vector>
#include <string>
#include <random>

class ClubAI {
public:
    ClubAI();
    ClubAI(unsigned int seed);

    std::vector<Player> select_lineup(Team& team);

    struct TransferDecision {
        bool should_buy = false;
        bool should_sell = false;
        int target_player_id = -1;
        int offer_price = 0;
        std::string reason;
        Position priority_position;
    };

    TransferDecision make_transfer_decision(Team& team, const std::vector<Player>& market);

    std::string adapt_tactics(const Team& team, const Team& opponent);

    void develop_player(Player& player, int delta_time);

private:
    std::mt19937 rng;

    Position find_weakest_position(const Team& team);
    bool needs_reinforcement(const Team& team, Position pos);
    double calculate_team_balance(const Team& team);
    int calculate_squad_depth(const Team& team, Position pos);

    std::string counter_formation(const std::string& opponent_formation);
    std::string counter_style(const std::string& opponent_style);

    void apply_physical_development(Player& player, int weeks);
    void apply_technical_development(Player& player, int weeks);
    void apply_mental_development(Player& player, int weeks);
    void apply_age_regression(Player& player, int weeks);

    int estimate_fair_price(const Player& player);
};
