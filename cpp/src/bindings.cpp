#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

#include "player.h"
#include "team.h"
#include "match_engine.h"
#include "club_ai.h"
#include "stat_calculator.h"

namespace py = pybind11;

PYBIND11_MODULE(game_core, m) {
    m.doc() = "Football Manager Game Core - C++ Engine";

    // Position enum
    py::enum_<Position>(m, "Position")
        .value("GK", Position::GK)
        .value("LB", Position::LB)
        .value("CB", Position::CB)
        .value("RB", Position::RB)
        .value("DM", Position::DM)
        .value("CM", Position::CM)
        .value("AM", Position::AM)
        .value("LW", Position::LW)
        .value("RW", Position::RW)
        .value("ST", Position::ST)
        .export_values();

    // EventType enum
    py::enum_<EventType>(m, "EventType")
        .value("GOAL", EventType::GOAL)
        .value("YELLOW_CARD", EventType::YELLOW_CARD)
        .value("RED_CARD", EventType::RED_CARD)
        .value("FOUL", EventType::FOUL)
        .value("SHOT", EventType::SHOT)
        .value("SAVE", EventType::SAVE)
        .value("CORNER", EventType::CORNER)
        .value("OFFSIDE", EventType::OFFSIDE)
        .value("INJURY", EventType::INJURY)
        .value("SUBSTITUTION", EventType::SUBSTITUTION)
        .value("PENALTY", EventType::PENALTY)
        .value("VAR", EventType::VAR)
        .export_values();

    // Player struct
    py::class_<Player>(m, "Player")
        .def(py::init<>())
        .def_readwrite("id", &Player::id)
        .def_readwrite("name", &Player::name)
        .def_readwrite("age", &Player::age)
        .def_readwrite("nationality", &Player::nationality)
        .def_readwrite("position", &Player::position)
        .def_readwrite("pace", &Player::pace)
        .def_readwrite("shooting", &Player::shooting)
        .def_readwrite("passing", &Player::passing)
        .def_readwrite("dribbling", &Player::dribbling)
        .def_readwrite("defending", &Player::defending)
        .def_readwrite("physical", &Player::physical)
        .def_readwrite("heading", &Player::heading)
        .def_readwrite("goalkeeping", &Player::goalkeeping)
        .def_readwrite("leadership", &Player::leadership)
        .def_readwrite("consistency", &Player::consistency)
        .def_readwrite("big_matches", &Player::big_matches)
        .def_readwrite("injury_tendency", &Player::injury_tendency)
        .def_readwrite("form", &Player::form)
        .def_readwrite("morale", &Player::morale)
        .def_readwrite("fatigue", &Player::fatigue)
        .def_readwrite("overall_rating", &Player::overall_rating)
        .def_readwrite("potential", &Player::potential)
        .def_readwrite("salary", &Player::salary)
        .def_readwrite("value", &Player::value)
        .def_readwrite("contract_years", &Player::contract_years)
        .def_property("traits",
            [](Player& p) -> std::vector<std::string>& { return p.traits; },
            [](Player& p, const std::vector<std::string>& t) { p.traits = t; })
        .def("calculate_overall", &Player::calculate_overall)
        .def("to_dict", &Player::to_dict)
        .def_static("from_dict", &Player::from_dict);

    // Team struct
    py::class_<Team>(m, "Team")
        .def(py::init<>())
        .def_readwrite("id", &Team::id)
        .def_readwrite("name", &Team::name)
        .def_readwrite("reputation", &Team::reputation)
        .def_readwrite("budget", &Team::budget)
        .def_readwrite("wage_budget", &Team::wage_budget)
        .def_readwrite("formation", &Team::formation)
        .def_readwrite("style", &Team::style)
        .def("get_players", [](Team& t) -> std::vector<Player>& { return t.players; }, py::return_value_policy::reference_internal)
        .def("set_players", [](Team& t, const std::vector<Player>& p) { t.players = p; })
        .def("get_starting_xi", &Team::get_starting_xi)
        .def("get_avg_rating", &Team::get_avg_rating)
        .def("get_team_strength", &Team::get_team_strength)
        .def("to_dict", &Team::to_dict);

    // MatchEvent struct
    py::class_<MatchEvent>(m, "MatchEvent")
        .def(py::init<>())
        .def_readwrite("minute", &MatchEvent::minute)
        .def_readwrite("event_type", &MatchEvent::event_type)
        .def_readwrite("player_name", &MatchEvent::player_name)
        .def_readwrite("team_id", &MatchEvent::team_id)
        .def_readwrite("detail", &MatchEvent::detail)
        .def_readwrite("xg_value", &MatchEvent::xg_value)
        .def("to_dict", &MatchEvent::to_dict);

    // MatchResult struct
    py::class_<MatchResult>(m, "MatchResult")
        .def(py::init<>())
        .def_readwrite("home_goals", &MatchResult::home_goals)
        .def_readwrite("away_goals", &MatchResult::away_goals)
        .def_readwrite("home_possession", &MatchResult::home_possession)
        .def_readwrite("away_possession", &MatchResult::away_possession)
        .def_readwrite("home_shots", &MatchResult::home_shots)
        .def_readwrite("away_shots", &MatchResult::away_shots)
        .def_readwrite("home_shots_on_target", &MatchResult::home_shots_on_target)
        .def_readwrite("away_shots_on_target", &MatchResult::away_shots_on_target)
        .def_readwrite("home_xg", &MatchResult::home_xg)
        .def_readwrite("away_xg", &MatchResult::away_xg)
        .def_property("events",
            [](MatchResult& r) -> std::vector<MatchEvent>& { return r.events; },
            [](MatchResult& r, const std::vector<MatchEvent>& e) { r.events = e; })
        .def_property("commentary_log",
            [](MatchResult& r) -> std::vector<std::string>& { return r.commentary_log; },
            [](MatchResult& r, const std::vector<std::string>& l) { r.commentary_log = l; })
        .def_readwrite("match_summary", &MatchResult::match_summary)
        .def_readwrite("man_of_the_match", &MatchResult::man_of_the_match)
        .def("to_dict", &MatchResult::to_dict);

    // MatchEngine class
    py::class_<MatchEngine>(m, "MatchEngine")
        .def(py::init<>())
        .def(py::init<unsigned int>())
        .def("simulate_match", &MatchEngine::simulate_match)
        .def("set_weather", &MatchEngine::set_weather)
        .def("set_surface", &MatchEngine::set_surface);

    // ClubAI class
    py::class_<ClubAI>(m, "ClubAI")
        .def(py::init<>())
        .def(py::init<unsigned int>())
        .def("select_lineup", &ClubAI::select_lineup)
        .def("make_transfer_decision", &ClubAI::make_transfer_decision)
        .def("adapt_tactics", &ClubAI::adapt_tactics)
        .def("develop_player", &ClubAI::develop_player);

    // ClubAI::TransferDecision nested struct
    py::class_<ClubAI::TransferDecision>(m, "TransferDecision")
        .def(py::init<>())
        .def_readwrite("should_buy", &ClubAI::TransferDecision::should_buy)
        .def_readwrite("should_sell", &ClubAI::TransferDecision::should_sell)
        .def_readwrite("target_player_id", &ClubAI::TransferDecision::target_player_id)
        .def_readwrite("offer_price", &ClubAI::TransferDecision::offer_price)
        .def_readwrite("reason", &ClubAI::TransferDecision::reason)
        .def_readwrite("priority_position", &ClubAI::TransferDecision::priority_position);

    // StatCalculator class
    py::class_<StatCalculator>(m, "StatCalculator")
        .def(py::init<>())
        .def(py::init<unsigned int>())
        .def("calculate_rating", &StatCalculator::calculate_rating)
        .def("calculate_value", &StatCalculator::calculate_value)
        .def("calculate_form", &StatCalculator::calculate_form, py::arg("recent_results"), py::arg("window") = 5)
        .def("calculate_fatigue", &StatCalculator::calculate_fatigue)
        .def("calculate_morale", &StatCalculator::calculate_morale)
        .def("age_regression", &StatCalculator::age_regression)
        .def("progress_young_player", &StatCalculator::progress_young_player);

    // Helper functions
    m.def("position_to_string", &position_to_string, "Convert Position enum to string");
    m.def("string_to_position", &string_to_position, "Convert string to Position enum");
    m.def("event_type_to_string", &event_type_to_string, "Convert EventType enum to string");
}
