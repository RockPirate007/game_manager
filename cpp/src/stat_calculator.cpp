#include "stat_calculator.h"
#include <algorithm>
#include <cmath>

StatCalculator::StatCalculator() : rng(std::random_device{}()) {}
StatCalculator::StatCalculator(unsigned int seed) : rng(seed) {}

int StatCalculator::calculate_rating(const Player& player) {
    double rating = 0;

    switch (player.position) {
        case Position::GK:
            rating = player.goalkeeping * 0.35 +
                     (player.pace + player.dribbling) / 2.0 * 0.20 +
                     player.physical * 0.15 +
                     player.passing * 0.10 +
                     player.leadership * 0.10 +
                     player.heading * 0.05 +
                     player.consistency * 0.05;
            break;
        case Position::CB:
            rating = player.defending * 0.30 +
                     player.physical * 0.20 +
                     player.heading * 0.15 +
                     player.pace * 0.10 +
                     player.passing * 0.10 +
                     player.shooting * 0.05 +
                     player.dribbling * 0.05 +
                     player.leadership * 0.05;
            break;
        case Position::LB:
        case Position::RB:
            rating = player.pace * 0.20 +
                     player.defending * 0.25 +
                     player.passing * 0.15 +
                     player.dribbling * 0.15 +
                     player.physical * 0.10 +
                     player.shooting * 0.05 +
                     player.heading * 0.05 +
                     (player.physical + player.pace) / 2.0 * 0.05;
            break;
        case Position::DM:
            rating = player.defending * 0.25 +
                     player.passing * 0.20 +
                     player.physical * 0.15 +
                     player.dribbling * 0.10 +
                     player.heading * 0.10 +
                     player.pace * 0.05 +
                     player.shooting * 0.05 +
                     player.leadership * 0.05 +
                     player.consistency * 0.05;
            break;
        case Position::CM:
            rating = player.passing * 0.20 +
                     player.dribbling * 0.15 +
                     player.defending * 0.15 +
                     player.shooting * 0.10 +
                     player.physical * 0.10 +
                     player.pace * 0.10 +
                     player.heading * 0.05 +
                     player.consistency * 0.10 +
                     player.leadership * 0.05;
            break;
        case Position::AM:
            rating = player.dribbling * 0.20 +
                     player.passing * 0.25 +
                     player.shooting * 0.15 +
                     player.pace * 0.10 +
                     player.physical * 0.05 +
                     player.heading * 0.05 +
                     player.consistency * 0.10 +
                     player.big_matches * 0.10;
            break;
        case Position::LW:
        case Position::RW:
            rating = player.pace * 0.20 +
                     player.dribbling * 0.25 +
                     player.shooting * 0.15 +
                     player.passing * 0.15 +
                     player.physical * 0.05 +
                     player.heading * 0.05 +
                     player.defending * 0.05 +
                     player.consistency * 0.10 +
                     player.big_matches * 0.05;
            break;
        case Position::ST:
            rating = player.shooting * 0.25 +
                     player.pace * 0.15 +
                     player.dribbling * 0.15 +
                     player.heading * 0.15 +
                     player.physical * 0.10 +
                     player.passing * 0.05 +
                     player.consistency * 0.10 +
                     player.big_matches * 0.05;
            break;
    }

    // Form modifier: 0.85 to 1.15
    double form_mod = 0.85 + (player.form / 100.0) * 0.30;
    rating *= form_mod;

    return clamp_stat(static_cast<int>(rating));
}

int StatCalculator::calculate_value(const Player& player, int market_state) {
    // Base value from rating
    double base = player.overall_rating * player.overall_rating * 100.0;

    // Age factor
    double age_factor = get_age_factor(player.age);
    base *= age_factor;

    // Potential factor
    double pot_factor = get_potential_factor(player.age, player.potential, player.overall_rating);
    base *= pot_factor;

    // Market state modifier (1.0 = normal)
    double market_mod = 1.0 + (market_state - 50) / 100.0;
    base *= market_mod;

    // Position premium (attacking players cost more)
    switch (player.position) {
        case Position::ST:
        case Position::AM:
        case Position::LW:
        case Position::RW:
            base *= 1.20;
            break;
        case Position::CM:
        case Position::DM:
            base *= 1.05;
            break;
        case Position::CB:
        case Position::LB:
        case Position::RB:
            base *= 0.95;
            break;
        case Position::GK:
            base *= 0.85;
            break;
    }

    // Contract length factor
    if (player.contract_years <= 1) base *= 0.50;
    else if (player.contract_years <= 2) base *= 0.75;
    else if (player.contract_years >= 5) base *= 1.10;

    // Reputation/nationality bonus
    if (!player.nationality.empty()) base *= 1.05;

    // Traits bonus
    base *= (1.0 + player.traits.size() * 0.02);

    // Morale factor
    double morale_mod = 0.90 + (player.morale / 100.0) * 0.20;
    base *= morale_mod;

    return std::max(10000, static_cast<int>(base));
}

int StatCalculator::calculate_form(const std::vector<int>& recent_results, int window) {
    if (recent_results.empty()) return 50;

    int start = std::max(0, static_cast<int>(recent_results.size()) - window);
    int sum = 0;
    int count = 0;
    for (int i = start; i < static_cast<int>(recent_results.size()); ++i) {
        // recent_results: +3 = win, +1 = draw, 0 = loss
        sum += recent_results[i];
        count++;
    }

    if (count == 0) return 50;

    double avg = static_cast<double>(sum) / count;
    // Map: 0 -> 20, 1 -> 45, 3 -> 85
    int form = static_cast<int>(20.0 + avg * 21.67);
    return clamp_stat(form);
}

int StatCalculator::calculate_fatigue(int matches_played, int rest_days, bool was_substituted) {
    // Base fatigue from matches
    int fatigue = matches_played * 12;

    // Rest reduces fatigue
    fatigue -= rest_days * 8;

    // Substitution reduces fatigue
    if (was_substituted) fatigue -= 10;

    return clamp_stat(std::max(0, fatigue));
}

int StatCalculator::calculate_morale(const std::vector<int>& results, int playing_time, int overall_rating) {
    // Recent results impact
    int recent_sum = 0;
    int window = std::min(5, static_cast<int>(results.size()));
    for (int i = static_cast<int>(results.size()) - window; i < static_cast<int>(results.size()); ++i) {
        if (i >= 0) recent_sum += results[i];
    }
    double result_morale = 50.0 + (recent_sum * 5.0);

    // Playing time impact (0-100 scale)
    double playing_morale = playing_time * 0.3;

    // Overall rating impact
    double rating_morale = overall_rating * 0.2;

    double total = result_morale * 0.5 + playing_morale * 0.3 + rating_morale * 0.2;
    return clamp_stat(static_cast<int>(total));
}

void StatCalculator::age_regression(Player& player, int weeks) {
    if (player.age < 30 || weeks <= 0) return;

    int years_over = player.age - 30;

    std::uniform_int_distribution<int> loss_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    // Physical regression accelerates
    int pace_loss_chance = 30 + years_over * 12;
    if (chance_dist(rng) < pace_loss_chance) {
        player.pace = std::max(1, player.pace - loss_dist(rng));
    }

    int phys_loss_chance = 25 + years_over * 10;
    if (chance_dist(rng) < phys_loss_chance) {
        player.physical = std::max(1, player.physical - loss_dist(rng));
    }

    // Technical stats slower decline
    if (years_over >= 2) {
        if (chance_dist(rng) < (10 + years_over * 5)) {
            player.dribbling = std::max(1, player.dribbling - 1);
        }
        if (chance_dist(rng) < (8 + years_over * 4)) {
            player.shooting = std::max(1, player.shooting - 1);
        }
    }

    // Mental stats may improve with age
    if (years_over <= 3) {
        if (chance_dist(rng) < 20) {
            player.leadership = std::min(99, player.leadership + 1);
        }
        if (chance_dist(rng) < 15) {
            player.consistency = std::min(99, player.consistency + 1);
        }
    }

    // Heading and defending decline slowly
    if (years_over >= 3 && chance_dist(rng) < (15 + years_over * 5)) {
        player.heading = std::max(1, player.heading - 1);
    }

    // Overall rating decline after 33
    if (player.age > 33) {
        int decline_chance = (player.age - 33) * 15;
        if (chance_dist(rng) < decline_chance) {
            player.overall_rating = std::max(30, player.overall_rating - 1);
        }
    }

    // Injury tendency increases
    if (years_over >= 2 && chance_dist(rng) < (5 + years_over * 3)) {
        player.injury_tendency = std::min(90, player.injury_tendency + 1);
    }

    player.calculate_overall();
}

void StatCalculator::progress_young_player(Player& player, int weeks) {
    if (player.age >= 24 || weeks <= 0) return;

    std::uniform_int_distribution<int> gain_dist(0, 2);
    std::uniform_int_distribution<int> chance_dist(0, 100);

    double potential_gap = player.potential - player.overall_rating;
    double growth_rate = potential_gap / (24.0 - player.age);

    // Higher potential = faster growth
    double pot_mod = 1.0;
    if (player.potential > 85) pot_mod = 1.3;
    else if (player.potential > 75) pot_mod = 1.15;
    else if (player.potential < 60) pot_mod = 0.7;

    // Technical development
    int tech_gain = 0;
    if (chance_dist(rng) < static_cast<int>(50 * pot_mod * growth_rate)) {
        tech_gain = gain_dist(rng);
    }

    if (tech_gain > 0) {
        switch (player.position) {
            case Position::GK:
                player.goalkeeping = std::min(99, player.goalkeeping + tech_gain);
                break;
            case Position::CB:
                player.defending = std::min(99, player.defending + tech_gain);
                if (chance_dist(rng) < 40) player.heading = std::min(99, player.heading + tech_gain);
                break;
            case Position::LB:
            case Position::RB:
                player.dribbling = std::min(99, player.dribbling + tech_gain);
                if (chance_dist(rng) < 50) player.passing = std::min(99, player.passing + tech_gain);
                break;
            case Position::DM:
                player.defending = std::min(99, player.defending + tech_gain);
                player.passing = std::min(99, player.passing + tech_gain);
                break;
            case Position::CM:
                player.passing = std::min(99, player.passing + tech_gain);
                if (chance_dist(rng) < 50) player.shooting = std::min(99, player.shooting + tech_gain);
                if (chance_dist(rng) < 50) player.dribbling = std::min(99, player.dribbling + tech_gain);
                break;
            case Position::AM:
                player.dribbling = std::min(99, player.dribbling + tech_gain);
                player.passing = std::min(99, player.passing + tech_gain);
                player.shooting = std::min(99, player.shooting + tech_gain);
                break;
            case Position::LW:
            case Position::RW:
                player.dribbling = std::min(99, player.dribbling + tech_gain);
                if (chance_dist(rng) < 50) player.shooting = std::min(99, player.shooting + tech_gain);
                break;
            case Position::ST:
                player.shooting = std::min(99, player.shooting + tech_gain);
                if (chance_dist(rng) < 50) player.dribbling = std::min(99, player.dribbling + tech_gain);
                break;
        }
    }

    // Physical development
    if (chance_dist(rng) < static_cast<int>(45 * pot_mod * growth_rate)) {
        int phys_gain = gain_dist(rng);
        player.pace = std::min(99, player.pace + phys_gain);
        if (chance_dist(rng) < 50) {
            player.physical = std::min(99, player.physical + phys_gain);
        }
    }

    // Mental development
    if (chance_dist(rng) < static_cast<int>(35 * pot_mod * growth_rate)) {
        int ment_gain = gain_dist(rng);
        if (chance_dist(rng) < 40) player.consistency = std::min(99, player.consistency + ment_gain);
        if (chance_dist(rng) < 30) player.big_matches = std::min(99, player.big_matches + ment_gain);
        if (chance_dist(rng) < 25) player.leadership = std::min(99, player.leadership + ment_gain);
    }

    // Recalculate overall
    player.calculate_overall();

    // Injury tendency improvement for young players
    if (player.age < 20 && chance_dist(rng) < 15) {
        player.injury_tendency = std::max(5, player.injury_tendency - 1);
    }
}

double StatCalculator::get_position_weight(const Player& player, const std::string& stat) {
    if (stat == "pace") {
        if (player.position == Position::LW || player.position == Position::RW) return 1.2;
        if (player.position == Position::ST) return 1.15;
        if (player.position == Position::GK) return 0.7;
        return 1.0;
    }
    if (stat == "shooting") {
        if (player.position == Position::ST) return 1.3;
        if (player.position == Position::AM) return 1.15;
        if (player.position == Position::GK) return 0.3;
        if (player.position == Position::CB) return 0.6;
        return 1.0;
    }
    if (stat == "passing") {
        if (player.position == Position::AM) return 1.2;
        if (player.position == Position::CM) return 1.15;
        if (player.position == Position::ST) return 0.8;
        return 1.0;
    }
    if (stat == "dribbling") {
        if (player.position == Position::LW || player.position == Position::RW) return 1.2;
        if (player.position == Position::AM) return 1.15;
        if (player.position == Position::GK) return 0.5;
        if (player.position == Position::CB) return 0.6;
        return 1.0;
    }
    if (stat == "defending") {
        if (player.position == Position::CB) return 1.3;
        if (player.position == Position::DM) return 1.2;
        if (player.position == Position::LB || player.position == Position::RB) return 1.1;
        if (player.position == Position::ST) return 0.4;
        return 1.0;
    }
    if (stat == "physical") {
        if (player.position == Position::CB) return 1.15;
        if (player.position == Position::ST) return 1.1;
        return 1.0;
    }
    if (stat == "heading") {
        if (player.position == Position::CB) return 1.2;
        if (player.position == Position::ST) return 1.15;
        return 0.9;
    }
    if (stat == "goalkeeping") {
        if (player.position == Position::GK) return 1.5;
        return 0.1;
    }
    return 1.0;
}

int StatCalculator::clamp_stat(int value) {
    return std::max(1, std::min(99, value));
}

double StatCalculator::get_age_factor(int age) {
    if (age < 18) return 0.6;
    if (age < 21) return 1.0;
    if (age < 24) return 1.3;
    if (age < 27) return 1.5;
    if (age < 30) return 1.2;
    if (age < 33) return 0.8;
    if (age < 36) return 0.5;
    return 0.3;
}

double StatCalculator::get_potential_factor(int /*age*/, int potential, int current) {
    double gap = potential - current;
    if (gap > 15) return 1.4;
    if (gap > 10) return 1.25;
    if (gap > 5) return 1.1;
    if (gap > 0) return 1.0;
    return 0.9;
}

int StatCalculator::estimate_market_modifier(int avg_reputation) {
    // Market state 50 = normal, >50 = inflated, <50 = deflated
    return 50 + (avg_reputation - 60) / 2;
}
