#pragma once

#include <string>
#include <vector>
#include <map>
#include <sstream>

enum class Position {
    GK, LB, CB, RB, DM, CM, AM, LW, RW, ST
};

inline std::string position_to_string(Position p) {
    switch (p) {
        case Position::GK: return "GK";
        case Position::LB: return "LB";
        case Position::CB: return "CB";
        case Position::RB: return "RB";
        case Position::DM: return "DM";
        case Position::CM: return "CM";
        case Position::AM: return "AM";
        case Position::LW: return "LW";
        case Position::RW: return "RW";
        case Position::ST: return "ST";
    }
    return "CM";
}

inline Position string_to_position(const std::string& s) {
    if (s == "GK") return Position::GK;
    if (s == "LB") return Position::LB;
    if (s == "CB") return Position::CB;
    if (s == "RB") return Position::RB;
    if (s == "DM") return Position::DM;
    if (s == "CM") return Position::CM;
    if (s == "AM") return Position::AM;
    if (s == "LW") return Position::LW;
    if (s == "RW") return Position::RW;
    if (s == "ST") return Position::ST;
    return Position::CM;
}

struct Player {
    int id = 0;
    std::string name;
    int age = 18;
    std::string nationality;
    Position position = Position::CM;

    // Football stats (0-100)
    int pace = 50;
    int shooting = 50;
    int passing = 50;
    int dribbling = 50;
    int defending = 50;
    int physical = 50;
    int heading = 50;
    int goalkeeping = 0;

    // Hidden stats (0-100)
    int leadership = 50;
    int consistency = 50;
    int big_matches = 50;
    int injury_tendency = 20;

    // Dynamic stats (0-100)
    int form = 50;
    int morale = 70;
    int fatigue = 0;
    int overall_rating = 50;
    int potential = 70;

    // Contract
    int salary = 10000;
    int value = 100000;
    int contract_years = 3;

    // Traits
    std::vector<std::string> traits;

    void calculate_overall() {
        switch (position) {
            case Position::GK:
                overall_rating = static_cast<int>(
                    goalkeeping * 0.35 + reflexes_factor() * 0.25 +
                    physical * 0.15 + passing * 0.10 + leadership * 0.10 +
                    heading * 0.05
                );
                break;
            case Position::CB:
                overall_rating = static_cast<int>(
                    defending * 0.30 + physical * 0.20 + heading * 0.15 +
                    pace * 0.10 + passing * 0.10 + shooting * 0.05 +
                    dribbling * 0.05 + leadership * 0.05
                );
                break;
            case Position::LB:
            case Position::RB:
                overall_rating = static_cast<int>(
                    pace * 0.20 + defending * 0.25 + passing * 0.15 +
                    dribbling * 0.15 + physical * 0.10 + shooting * 0.05 +
                    heading * 0.05 + stamina_factor() * 0.05
                );
                break;
            case Position::DM:
                overall_rating = static_cast<int>(
                    defending * 0.25 + passing * 0.20 + physical * 0.15 +
                    dribbling * 0.10 + heading * 0.10 + pace * 0.05 +
                    shooting * 0.05 + leadership * 0.05 + consistency * 0.05
                );
                break;
            case Position::CM:
                overall_rating = static_cast<int>(
                    passing * 0.20 + dribbling * 0.15 + defending * 0.15 +
                    shooting * 0.10 + physical * 0.10 + pace * 0.10 +
                    heading * 0.05 + consistency * 0.10 + leadership * 0.05
                );
                break;
            case Position::AM:
                overall_rating = static_cast<int>(
                    dribbling * 0.20 + passing * 0.25 + shooting * 0.15 +
                    pace * 0.10 + physical * 0.05 + heading * 0.05 +
                    consistency * 0.10 + big_matches * 0.10
                );
                break;
            case Position::LW:
            case Position::RW:
                overall_rating = static_cast<int>(
                    pace * 0.20 + dribbling * 0.25 + shooting * 0.15 +
                    passing * 0.15 + physical * 0.05 + heading * 0.05 +
                    defending * 0.05 + consistency * 0.10 + big_matches * 0.05
                );
                break;
            case Position::ST:
                overall_rating = static_cast<int>(
                    shooting * 0.25 + pace * 0.15 + dribbling * 0.15 +
                    heading * 0.15 + physical * 0.10 + passing * 0.05 +
                    consistency * 0.10 + big_matches * 0.05
                );
                break;
        }

        // Apply form modifier
        double form_modifier = 0.85 + (form / 100.0) * 0.30;
        overall_rating = static_cast<int>(overall_rating * form_modifier);

        // Clamp
        if (overall_rating > 99) overall_rating = 99;
        if (overall_rating < 1) overall_rating = 1;
    }

    std::map<std::string, std::string> to_dict() const {
        std::map<std::string, std::string> d;
        d["id"] = std::to_string(id);
        d["name"] = name;
        d["age"] = std::to_string(age);
        d["nationality"] = nationality;
        d["position"] = position_to_string(position);
        d["pace"] = std::to_string(pace);
        d["shooting"] = std::to_string(shooting);
        d["passing"] = std::to_string(passing);
        d["dribbling"] = std::to_string(dribbling);
        d["defending"] = std::to_string(defending);
        d["physical"] = std::to_string(physical);
        d["heading"] = std::to_string(heading);
        d["goalkeeping"] = std::to_string(goalkeeping);
        d["leadership"] = std::to_string(leadership);
        d["consistency"] = std::to_string(consistency);
        d["big_matches"] = std::to_string(big_matches);
        d["injury_tendency"] = std::to_string(injury_tendency);
        d["form"] = std::to_string(form);
        d["morale"] = std::to_string(morale);
        d["fatigue"] = std::to_string(fatigue);
        d["overall_rating"] = std::to_string(overall_rating);
        d["potential"] = std::to_string(potential);
        d["salary"] = std::to_string(salary);
        d["value"] = std::to_string(value);
        d["contract_years"] = std::to_string(contract_years);
        std::string traits_str;
        for (size_t i = 0; i < traits.size(); ++i) {
            if (i > 0) traits_str += ",";
            traits_str += traits[i];
        }
        d["traits"] = traits_str;
        return d;
    }

    static Player from_dict(const std::map<std::string, std::string>& d) {
        Player p;
        if (d.count("id")) p.id = std::stoi(d.at("id"));
        if (d.count("name")) p.name = d.at("name");
        if (d.count("age")) p.age = std::stoi(d.at("age"));
        if (d.count("nationality")) p.nationality = d.at("nationality");
        if (d.count("position")) p.position = string_to_position(d.at("position"));
        if (d.count("pace")) p.pace = std::stoi(d.at("pace"));
        if (d.count("shooting")) p.shooting = std::stoi(d.at("shooting"));
        if (d.count("passing")) p.passing = std::stoi(d.at("passing"));
        if (d.count("dribbling")) p.dribbling = std::stoi(d.at("dribbling"));
        if (d.count("defending")) p.defending = std::stoi(d.at("defending"));
        if (d.count("physical")) p.physical = std::stoi(d.at("physical"));
        if (d.count("heading")) p.heading = std::stoi(d.at("heading"));
        if (d.count("goalkeeping")) p.goalkeeping = std::stoi(d.at("goalkeeping"));
        if (d.count("leadership")) p.leadership = std::stoi(d.at("leadership"));
        if (d.count("consistency")) p.consistency = std::stoi(d.at("consistency"));
        if (d.count("big_matches")) p.big_matches = std::stoi(d.at("big_matches"));
        if (d.count("injury_tendency")) p.injury_tendency = std::stoi(d.at("injury_tendency"));
        if (d.count("form")) p.form = std::stoi(d.at("form"));
        if (d.count("morale")) p.morale = std::stoi(d.at("morale"));
        if (d.count("fatigue")) p.fatigue = std::stoi(d.at("fatigue"));
        if (d.count("overall_rating")) p.overall_rating = std::stoi(d.at("overall_rating"));
        if (d.count("potential")) p.potential = std::stoi(d.at("potential"));
        if (d.count("salary")) p.salary = std::stoi(d.at("salary"));
        if (d.count("value")) p.value = std::stoi(d.at("value"));
        if (d.count("contract_years")) p.contract_years = std::stoi(d.at("contract_years"));
        if (d.count("traits")) {
            std::istringstream ss(d.at("traits"));
            std::string token;
            while (std::getline(ss, token, ',')) {
                if (!token.empty()) p.traits.push_back(token);
            }
        }
        return p;
    }

    double reflexes_factor() const {
        return static_cast<double>(pace + dribbling) / 2.0;
    }

    double stamina_factor() const {
        return static_cast<double>(physical + pace) / 2.0;
    }
};
