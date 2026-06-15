#include "club_ai.h"
#include <algorithm>
#include <cmath>
#include <sstream>

ClubAI::ClubAI() : rng(std::random_device{}()) {}
ClubAI::ClubAI(unsigned int seed) : rng(seed) {}

std::vector<Player> ClubAI::select_lineup(Team& team) {
    return team.get_starting_xi();
}

ClubAI::TransferDecision ClubAI::make_transfer_decision(Team& team, const std::vector<Player>& market) {
    TransferDecision decision;

    Position weakest = find_weakest_position(team);

    // Check if we need reinforcement
    int depth = calculate_squad_depth(team, weakest);
    if (depth < 2) {
        decision.should_buy = true;
        decision.priority_position = weakest;
        decision.reason = "Недостаточно глубины на позиции " + position_to_string(weakest);
    }

    // Check for players with expiring contracts (value < threshold)
    for (const auto& p : team.players) {
        if (p.contract_years <= 1 && p.overall_rating > 60) {
            decision.should_sell = true;
            decision.target_player_id = p.id;
            decision.offer_price = estimate_fair_price(p);
            decision.reason = "Контракт " + p.name + " истекает через " +
                              std::to_string(p.contract_years) + " год(а)";
            break;
        }
    }

    // Budget considerations
    if (team.budget < team.wage_budget * 6) {
        // Low budget - sell high-value players
        int highest_value = 0;
        int highest_id = -1;
        std::string highest_name;
        for (const auto& p : team.players) {
            if (p.value > highest_value && p.contract_years <= 2) {
                highest_value = p.value;
                highest_id = p.id;
                highest_name = p.name;
            }
        }
        if (highest_id != -1) {
            decision.should_sell = true;
            decision.target_player_id = highest_id;
            decision.offer_price = static_cast<int>(highest_value * 1.2);
            decision.reason = "Необходимо пополнить бюджет. Продажа " + highest_name;
        }
    }

    // Find best target from market
    if (decision.should_buy) {
        int best_id = -1;
        int best_value = 0;
        for (const auto& p : market) {
            if (p.position == decision.priority_position &&
                p.value <= team.budget * 0.3 &&
                p.overall_rating > 60) {
                int score = p.overall_rating * 2 + p.potential - p.age;
                if (score > best_value) {
                    best_value = score;
                    best_id = p.id;
                    decision.target_player_id = best_id;
                    decision.offer_price = estimate_fair_price(p);
                }
            }
        }
    }

    return decision;
}

std::string ClubAI::adapt_tactics(const Team& team, const Team& opponent) {
    // Analyze opponent
    std::string opp_formation = opponent.formation;
    std::string opp_style = opponent.style;

    std::string new_style = team.style;

    // Counter their formation
    if (opp_formation == "4-3-3" || opp_formation == "4-2-3-1") {
        // They attack wide, we compact middle
        new_style = "defensive";
    } else if (opp_formation == "3-5-2" || opp_formation == "3-4-3") {
        // They overload midfield, we counter on wings
        new_style = "counter";
    } else if (opp_formation == "5-3-2" || opp_formation == "5-4-1") {
        // They park the bus, we need possession
        new_style = "possession";
    }

    // Counter their style
    if (opp_style == "attacking") {
        new_style = "counter";
    } else if (opp_style == "possession") {
        new_style = "pressing";
    } else if (opp_style == "defensive") {
        new_style = "wing_play";
    } else if (opp_style == "pressing") {
        new_style = "possession";
    }

    // Consider our own strengths
    auto xi = const_cast<Team&>(team).get_starting_xi();
    int avg_pace = 0;
    int avg_technique = 0;
    for (const auto& p : xi) {
        avg_pace += p.pace;
        avg_technique += (p.dribbling + p.passing) / 2;
    }
    avg_pace /= static_cast<int>(xi.size());
    avg_technique /= static_cast<int>(xi.size());

    if (avg_pace > 75 && new_style != "counter") {
        new_style = "counter";
    }
    if (avg_technique > 75 && new_style != "possession") {
        new_style = "possession";
    }

    // Reputation-based confidence
    if (team.reputation > opponent.reputation + 20) {
        new_style = "attacking";
    } else if (team.reputation < opponent.reputation - 20) {
        new_style = "defensive";
    }

    return new_style;
}

void ClubAI::develop_player(Player& player, int delta_time) {
    int weeks = delta_time;

    // Apply age-based regression for older players
    apply_age_regression(player, weeks);

    // Young players develop faster
    if (player.age < 21) {
        apply_technical_development(player, weeks);
        apply_physical_development(player, weeks);
        apply_mental_development(player, weeks);
    } else if (player.age < 26) {
        // Peak development
        apply_technical_development(player, weeks);
        apply_physical_development(player, weeks);
        apply_mental_development(player, weeks);
    } else if (player.age < 30) {
        // Slower development
        apply_mental_development(player, weeks);
        // Slight technical improvement
        if (weeks > 0) {
            std::uniform_int_distribution<int> dist(0, 1);
            if (dist(rng) == 0) {
                player.passing = std::min(99, player.passing + (weeks > 4 ? 1 : 0));
            }
        }
    }

    // Potential ceiling
    if (player.overall_rating > player.potential) {
        player.overall_rating = player.potential;
    }

    // Recalculate overall
    player.calculate_overall();

    // Morale boost for development
    if (player.overall_rating >= player.potential - 2) {
        player.morale = std::min(100, player.morale + 2);
    }
}

Position ClubAI::find_weakest_position(const Team& team) {
    std::map<Position, double> pos_ratings;
    std::map<Position, int> pos_counts;

    for (const auto& p : team.players) {
        pos_ratings[p.position] += p.overall_rating;
        pos_counts[p.position]++;
    }

    Position weakest = Position::CM;
    double lowest_avg = 100.0;

    for (auto& [pos, total] : pos_ratings) {
        double avg = total / pos_counts[pos];
        if (avg < lowest_avg) {
            lowest_avg = avg;
            weakest = pos;
        }
    }

    return weakest;
}

bool ClubAI::needs_reinforcement(const Team& team, Position pos) {
    int count = 0;
    int total_rating = 0;
    for (const auto& p : team.players) {
        if (p.position == pos) {
            count++;
            total_rating += p.overall_rating;
        }
    }
    if (count < 2) return true;
    if (total_rating / count < 65) return true;
    return false;
}

double ClubAI::calculate_team_balance(const Team& team) {
    std::map<Position, int> pos_counts;
    for (const auto& p : team.players) {
        pos_counts[p.position]++;
    }

    int gk = pos_counts[Position::GK];
    int def = pos_counts[Position::CB] + pos_counts[Position::LB] + pos_counts[Position::RB];
    int mid = pos_counts[Position::DM] + pos_counts[Position::CM] + pos_counts[Position::AM];
    int att = pos_counts[Position::LW] + pos_counts[Position::RW] + pos_counts[Position::ST];

    double balance = 1.0;
    if (gk < 2) balance -= 0.15;
    if (def < 6) balance -= 0.10;
    if (mid < 5) balance -= 0.10;
    if (att < 3) balance -= 0.10;

    return std::max(0.0, balance);
}

int ClubAI::calculate_squad_depth(const Team& team, Position pos) {
    int count = 0;
    for (const auto& p : team.players) {
        if (p.position == pos) count++;
    }
    return count;
}

std::string ClubAI::counter_formation(const std::string& opponent_formation) {
    if (opponent_formation == "4-4-2") return "4-5-1";
    if (opponent_formation == "4-3-3") return "4-5-1";
    if (opponent_formation == "3-5-2") return "4-3-3";
    if (opponent_formation == "4-2-3-1") return "4-4-2";
    if (opponent_formation == "5-3-2") return "4-3-3";
    return "4-4-2";
}

std::string ClubAI::counter_style(const std::string& opponent_style) {
    if (opponent_style == "attacking") return "counter";
    if (opponent_style == "possession") return "pressing";
    if (opponent_style == "defensive") return "possession";
    if (opponent_style == "counter") return "possession";
    if (opponent_style == "pressing") return "direct";
    if (opponent_style == "wing_play") return "defensive";
    if (opponent_style == "direct") return "possession";
    return "balanced";
}

void ClubAI::apply_physical_development(Player& player, int weeks) {
    if (weeks <= 0) return;

    std::uniform_int_distribution<int> gain_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    // Young players gain physical stats
    if (player.age < 23) {
        if (chance_dist(rng) < 60) player.pace = std::min(99, player.pace + gain_dist(rng));
        if (chance_dist(rng) < 60) player.physical = std::min(99, player.physical + gain_dist(rng));
        if (chance_dist(rng) < 40) player.heading = std::min(99, player.heading + gain_dist(rng));
    }
    // Mature players maintain
    else if (player.age < 30) {
        if (chance_dist(rng) < 20) player.pace = std::min(99, player.pace + (gain_dist(rng) > 1 ? 1 : 0));
        if (chance_dist(rng) < 25) player.physical = std::min(99, player.physical + (gain_dist(rng) > 1 ? 1 : 0));
    }
}

void ClubAI::apply_technical_development(Player& player, int weeks) {
    if (weeks <= 0) return;

    std::uniform_int_distribution<int> gain_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    if (player.age < 23) {
        if (chance_dist(rng) < 55) player.shooting = std::min(99, player.shooting + gain_dist(rng));
        if (chance_dist(rng) < 55) player.passing = std::min(99, player.passing + gain_dist(rng));
        if (chance_dist(rng) < 55) player.dribbling = std::min(99, player.dribbling + gain_dist(rng));
        if (player.position == Position::GK && chance_dist(rng) < 50) {
            player.goalkeeping = std::min(99, player.goalkeeping + gain_dist(rng));
        }
    } else if (player.age < 28) {
        if (chance_dist(rng) < 30) player.shooting = std::min(99, player.shooting + (gain_dist(rng) > 1 ? 1 : 0));
        if (chance_dist(rng) < 30) player.passing = std::min(99, player.passing + (gain_dist(rng) > 1 ? 1 : 0));
    }
}

void ClubAI::apply_mental_development(Player& player, int weeks) {
    if (weeks <= 0) return;

    std::uniform_int_distribution<int> gain_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    // Mental stats improve with age and experience
    if (player.age < 25) {
        if (chance_dist(rng) < 40) player.leadership = std::min(99, player.leadership + gain_dist(rng));
        if (chance_dist(rng) < 40) player.consistency = std::min(99, player.consistency + gain_dist(rng));
        if (chance_dist(rng) < 35) player.big_matches = std::min(99, player.big_matches + gain_dist(rng));
    } else if (player.age < 32) {
        if (chance_dist(rng) < 25) player.leadership = std::min(99, player.leadership + (gain_dist(rng) > 1 ? 1 : 0));
        if (chance_dist(rng) < 25) player.consistency = std::min(99, player.consistency + (gain_dist(rng) > 1 ? 1 : 0));
    }
}

void ClubAI::apply_age_regression(Player& player, int weeks) {
    if (player.age < 30 || weeks <= 0) return;

    int years_over = player.age - 30;
    std::uniform_int_distribution<int> loss_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    // Physical decline accelerates with age
    if (years_over >= 1 && chance_dist(rng) < (30 + years_over * 10)) {
        player.pace = std::max(1, player.pace - loss_dist(rng));
    }
    if (years_over >= 2 && chance_dist(rng) < (25 + years_over * 8)) {
        player.physical = std::max(1, player.physical - loss_dist(rng));
    }
    if (years_over >= 1 && chance_dist(rng) < (20 + years_over * 5)) {
        player.dribbling = std::max(1, player.dribbling - (loss_dist(rng) > 1 ? 1 : 0));
    }

    // Mental stats may improve or maintain
    if (years_over <= 3 && chance_dist(rng) < 20) {
        player.leadership = std::min(99, player.leadership + 1);
    }

    // Overall rating decline
    if (years_over > 2 && chance_dist(rng) < (years_over * 8)) {
        player.overall_rating = std::max(30, player.overall_rating - 1);
    }
}

int ClubAI::estimate_fair_price(const Player& player) {
    double base = player.overall_rating * player.overall_rating * 100.0;

    // Age factor
    if (player.age < 23) base *= 1.5;
    else if (player.age < 27) base *= 1.2;
    else if (player.age < 30) base *= 1.0;
    else if (player.age < 33) base *= 0.6;
    else base *= 0.3;

    // Potential bonus
    int pot_diff = player.potential - player.overall_rating;
    if (pot_diff > 10) base *= 1.3;
    else if (pot_diff > 5) base *= 1.15;

    // Contract length discount
    if (player.contract_years <= 1) base *= 0.5;
    else if (player.contract_years <= 2) base *= 0.75;

    // National team bonus
    if (!player.nationality.empty()) base *= 1.1;

    return static_cast<int>(base);
}
