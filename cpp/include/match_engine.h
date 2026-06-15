#pragma once

#include "team.h"
#include <vector>
#include <string>
#include <random>
#include <map>

enum class EventType {
    GOAL,
    YELLOW_CARD,
    RED_CARD,
    FOUL,
    SHOT,
    SAVE,
    CORNER,
    OFFSIDE,
    INJURY,
    SUBSTITUTION,
    PENALTY,
    VAR
};

inline std::string event_type_to_string(EventType t) {
    switch (t) {
        case EventType::GOAL: return "goal";
        case EventType::YELLOW_CARD: return "yellow_card";
        case EventType::RED_CARD: return "red_card";
        case EventType::FOUL: return "foul";
        case EventType::SHOT: return "shot";
        case EventType::SAVE: return "save";
        case EventType::CORNER: return "corner";
        case EventType::OFFSIDE: return "offside";
        case EventType::INJURY: return "injury";
        case EventType::SUBSTITUTION: return "substitution";
        case EventType::PENALTY: return "penalty";
        case EventType::VAR: return "var";
    }
    return "unknown";
}

struct MatchEvent {
    int minute = 0;
    EventType event_type = EventType::FOUL;
    std::string player_name;
    int team_id = 0;
    std::string detail;
    double xg_value = 0.0;

    std::map<std::string, std::string> to_dict() const {
        std::map<std::string, std::string> d;
        d["minute"] = std::to_string(minute);
        d["event_type"] = event_type_to_string(event_type);
        d["player_name"] = player_name;
        d["team_id"] = std::to_string(team_id);
        d["detail"] = detail;
        d["xg_value"] = std::to_string(xg_value);
        return d;
    }
};

struct MatchResult {
    int home_goals = 0;
    int away_goals = 0;
    double home_possession = 50.0;
    double away_possession = 50.0;
    int home_shots = 0;
    int away_shots = 0;
    int home_shots_on_target = 0;
    int away_shots_on_target = 0;
    double home_xg = 0.0;
    double away_xg = 0.0;
    std::vector<MatchEvent> events;
    std::vector<std::string> commentary_log;
    std::string match_summary;
    std::string man_of_the_match;

    std::map<std::string, std::string> to_dict() const {
        std::map<std::string, std::string> d;
        d["home_goals"] = std::to_string(home_goals);
        d["away_goals"] = std::to_string(away_goals);
        d["home_possession"] = std::to_string(home_possession);
        d["away_possession"] = std::to_string(away_possession);
        d["home_shots"] = std::to_string(home_shots);
        d["away_shots"] = std::to_string(away_shots);
        d["home_shots_on_target"] = std::to_string(home_shots_on_target);
        d["away_shots_on_target"] = std::to_string(away_shots_on_target);
        d["home_xg"] = std::to_string(home_xg);
        d["away_xg"] = std::to_string(away_xg);
        d["match_summary"] = match_summary;
        d["man_of_the_match"] = man_of_the_match;
        d["event_count"] = std::to_string(events.size());
        return d;
    }
};

class MatchEngine {
public:
    MatchEngine();
    MatchEngine(unsigned int seed);

    MatchResult simulate_match(Team& home_team, Team& away_team);

    void set_weather(const std::string& weather);
    void set_surface(const std::string& surface);

private:
    std::mt19937 rng;
    std::string weather = "clear";
    std::string surface = "good";

    double calculate_possession(const Team& home, const Team& away);
    double calculate_attack_strength(const Team& team, double possession);
    double calculate_defense_strength(const Team& team);
    double calculate_xg(double attack_strength, double defense_strength, int situation);
    EventType determine_event_type(double random_val, bool is_home);

    std::string generate_commentary(const MatchEvent& event, const std::string& home_name, const std::string& away_name);
    std::string generate_match_summary(const MatchResult& result, const std::string& home_name, const std::string& away_name);
    std::string pick_motm(const MatchResult& result, const std::vector<Player>& home_xi, const std::vector<Player>& away_xi);

    double get_tactical_modifier(const std::string& style, const std::string& aspect);
    int get_pace_factor(const Team& team);
    Player* find_random_player(std::vector<Player>& players, Position pos);
    Player* find_random_attacker(std::vector<Player>& players);
    Player* find_random_midfielder(std::vector<Player>& players);
    Player* find_random_defender(std::vector<Player>& players);
    Player* find_goalkeeper(std::vector<Player>& players);
};
