#pragma once

#include "player.h"
#include <vector>
#include <map>
#include <algorithm>
#include <numeric>
#include <string>

struct Team {
    int id = 0;
    std::string name;
    int reputation = 50;
    int budget = 10000000;
    int wage_budget = 500000;

    std::vector<Player> players;

    std::string formation = "4-4-2";
    std::string style = "balanced";

    std::vector<Player> get_starting_xi() const {
        std::vector<Player> sorted_players = players;
        std::vector<Player> starting_xi;

        std::vector<Position> gk_slots = {Position::GK};
        std::vector<Position> def_slots;
        std::vector<Position> mid_slots;
        std::vector<Position> att_slots;

        parse_formation(def_slots, mid_slots, att_slots);

        auto pick_best_for = [&](const std::vector<Position>& positions, int count) {
            std::vector<Player> candidates;
            for (auto& p : sorted_players) {
                for (auto pos : positions) {
                    if (p.position == pos) {
                        bool already_selected = false;
                        for (auto& sel : starting_xi) {
                            if (sel.id == p.id) { already_selected = true; break; }
                        }
                        if (!already_selected) {
                            candidates.push_back(p);
                            break;
                        }
                    }
                }
            }
            std::sort(candidates.begin(), candidates.end(),
                [](const Player& a, const Player& b) {
                    return a.overall_rating > b.overall_rating;
                });
            for (int i = 0; i < count && i < static_cast<int>(candidates.size()); ++i) {
                starting_xi.push_back(candidates[i]);
            }
        };

        pick_best_for(gk_slots, 1);
        pick_best_for(def_slots, static_cast<int>(def_slots.size()));
        pick_best_for(mid_slots, static_cast<int>(mid_slots.size()));
        pick_best_for(att_slots, static_cast<int>(att_slots.size()));

        // Fill remaining spots with best available
        while (static_cast<int>(starting_xi.size()) < 11) {
            Player* best = nullptr;
            for (auto& p : sorted_players) {
                bool in_xi = false;
                for (auto& sel : starting_xi) {
                    if (sel.id == p.id) { in_xi = true; break; }
                }
                if (!in_xi) {
                    if (!best || p.overall_rating > best->overall_rating) {
                        best = &p;
                    }
                }
            }
            if (best) {
                starting_xi.push_back(*best);
            } else {
                break;
            }
        }

        return starting_xi;
    }

    double get_avg_rating() const {
        if (players.empty()) return 0.0;
        double total = 0.0;
        for (const auto& p : players) {
            total += p.overall_rating;
        }
        return total / players.size();
    }

    double get_team_strength() const {
        auto xi = get_starting_xi();
        if (xi.empty()) return 0.0;
        double total = 0.0;
        for (const auto& p : xi) {
            total += p.overall_rating;
        }
        return total / xi.size();
    }

    std::map<std::string, std::string> to_dict() const {
        std::map<std::string, std::string> d;
        d["id"] = std::to_string(id);
        d["name"] = name;
        d["reputation"] = std::to_string(reputation);
        d["budget"] = std::to_string(budget);
        d["wage_budget"] = std::to_string(wage_budget);
        d["formation"] = formation;
        d["style"] = style;
        d["player_count"] = std::to_string(players.size());
        d["avg_rating"] = std::to_string(get_avg_rating());
        return d;
    }

private:
    void parse_formation(std::vector<Position>& defs, std::vector<Position>& mids, std::vector<Position>& atts) const {
        // Parse formations like "4-4-2", "4-3-3", "3-5-2", etc.
        std::vector<int> nums;
        std::istringstream ss(formation);
        std::string token;
        while (std::getline(ss, token, '-')) {
            nums.push_back(std::stoi(token));
        }

        if (nums.size() < 3) {
            // Default to 4-4-2
            nums = {4, 4, 2};
        }

        int def_count = nums[0];
        int mid_count = nums[1];
        int att_count = nums[2];

        // Distribute defenders
        if (def_count == 3) {
            defs = {Position::CB, Position::CB, Position::CB};
        } else if (def_count == 4) {
            defs = {Position::LB, Position::CB, Position::CB, Position::RB};
        } else if (def_count == 5) {
            defs = {Position::LB, Position::CB, Position::CB, Position::CB, Position::RB};
        } else {
            for (int i = 0; i < def_count; ++i) defs.push_back(Position::CB);
        }

        // Distribute midfielders
        if (mid_count == 3) {
            mids = {Position::DM, Position::CM, Position::AM};
        } else if (mid_count == 4) {
            mids = {Position::LW, Position::CM, Position::CM, Position::RW};
        } else if (mid_count == 5) {
            mids = {Position::LW, Position::DM, Position::CM, Position::AM, Position::RW};
        } else {
            for (int i = 0; i < mid_count; ++i) mids.push_back(Position::CM);
        }

        // Distribute attackers
        if (att_count == 1) {
            atts = {Position::ST};
        } else if (att_count == 2) {
            atts = {Position::ST, Position::ST};
        } else if (att_count == 3) {
            atts = {Position::LW, Position::ST, Position::RW};
        } else {
            for (int i = 0; i < att_count; ++i) atts.push_back(Position::ST);
        }
    }
};
