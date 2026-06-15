#include "match_engine.h"
#include <algorithm>
#include <cmath>
#include <sstream>
#include <iomanip>

MatchEngine::MatchEngine() : rng(std::random_device{}()) {}
MatchEngine::MatchEngine(unsigned int seed) : rng(seed) {}

void MatchEngine::set_weather(const std::string& w) { weather = w; }
void MatchEngine::set_surface(const std::string& s) { surface = s; }

double MatchEngine::calculate_possession(const Team& home, const Team& away) {
    double home_pass = 0, away_pass = 0;
    auto home_xi = const_cast<Team&>(home).get_starting_xi();
    auto away_xi = const_cast<Team&>(away).get_starting_xi();

    for (auto& p : home_xi) home_pass += p.passing + p.dribbling;
    for (auto& p : away_xi) away_pass += p.passing + p.dribbling;

    double home_adv = 1.08;
    double home_style_mod = get_tactical_modifier(home.style, "possession");
    double away_style_mod = get_tactical_modifier(away.style, "possession");

    double home_total = (home_pass / 11.0) * home_adv * home_style_mod;
    double away_total = (away_pass / 11.0) * away_style_mod;

    double total = home_total + away_total;
    if (total == 0) return 50.0;
    return (home_total / total) * 100.0;
}

double MatchEngine::calculate_attack_strength(const Team& team, double possession) {
    auto xi = const_cast<Team&>(team).get_starting_xi();
    double attack = 0;
    for (auto& p : xi) {
        if (p.position == Position::ST || p.position == Position::AM ||
            p.position == Position::LW || p.position == Position::RW) {
            attack += (p.shooting + p.dribbling + p.pace + p.heading) / 4.0;
        } else if (p.position == Position::CM || p.position == Position::DM) {
            attack += (p.passing + p.dribbling) / 6.0;
        }
    }

    double form_bonus = 0;
    for (auto& p : xi) form_bonus += p.form;
    form_bonus = (form_bonus / (11.0 * 100.0)) * 10.0;

    double pos_factor = possession / 100.0;
    double style_mod = get_tactical_modifier(team.style, "attack");

    return (attack / 11.0) + form_bonus + (pos_factor * 5.0) * style_mod;
}

double MatchEngine::calculate_defense_strength(const Team& team) {
    auto xi = const_cast<Team&>(team).get_starting_xi();
    double defense = 0;
    for (auto& p : xi) {
        if (p.position == Position::CB || p.position == Position::LB || p.position == Position::RB) {
            defense += (p.defending + p.physical + p.heading) / 3.0;
        } else if (p.position == Position::GK) {
            defense += (p.goalkeeping + p.reflexes_factor()) / 2.0;
        } else if (p.position == Position::DM) {
            defense += (p.defending + p.physical) / 4.0;
        }
    }

    double style_mod = get_tactical_modifier(team.style, "defense");
    return (defense / 11.0) * style_mod;
}

double MatchEngine::calculate_xg(double attack_strength, double defense_strength, int situation) {
    // situation: 0=open play, 1=counter, 2=set piece, 3=penalty
    double base_xg = 0.08;
    if (situation == 1) base_xg = 0.12;
    if (situation == 2) base_xg = 0.10;
    if (situation == 3) base_xg = 0.76;

    double strength_ratio = attack_strength / (attack_strength + defense_strength + 0.001);
    double xg = base_xg * (0.5 + strength_ratio);

    // Weather impact
    if (weather == "rain") xg *= 0.92;
    if (weather == "snow") xg *= 0.85;
    if (weather == "wind") xg *= 0.88;

    // Surface impact
    if (surface == "poor") xg *= 0.90;
    if (surface == "wet") xg *= 0.93;

    if (xg > 0.95) xg = 0.95;
    if (xg < 0.01) xg = 0.01;

    return xg;
}

EventType MatchEngine::determine_event_type(double random_val, bool /*is_home*/) {
    if (random_val < 0.02) return EventType::GOAL;
    if (random_val < 0.06) return EventType::YELLOW_CARD;
    if (random_val < 0.07) return EventType::RED_CARD;
    if (random_val < 0.15) return EventType::FOUL;
    if (random_val < 0.30) return EventType::SHOT;
    if (random_val < 0.35) return EventType::SAVE;
    if (random_val < 0.42) return EventType::CORNER;
    if (random_val < 0.47) return EventType::OFFSIDE;
    if (random_val < 0.49) return EventType::INJURY;
    if (random_val < 0.50) return EventType::SUBSTITUTION;
    if (random_val < 0.51) return EventType::PENALTY;
    return EventType::VAR;
}

Player* MatchEngine::find_goalkeeper(std::vector<Player>& players) {
    for (auto& p : players) {
        if (p.position == Position::GK) return &p;
    }
    return players.empty() ? nullptr : &players[0];
}

Player* MatchEngine::find_random_player(std::vector<Player>& players, Position pos) {
    std::vector<Player*> candidates;
    for (auto& p : players) {
        if (p.position == pos) candidates.push_back(&p);
    }
    if (candidates.empty()) {
        for (auto& p : players) candidates.push_back(&p);
    }
    if (candidates.empty()) return nullptr;
    std::uniform_int_distribution<size_t> dist(0, candidates.size() - 1);
    return candidates[dist(rng)];
}

Player* MatchEngine::find_random_attacker(std::vector<Player>& players) {
    for (int attempts = 0; attempts < 20; ++attempts) {
        Player* p = find_random_player(players, Position::ST);
        if (p) return p;
    }
    for (int attempts = 0; attempts < 20; ++attempts) {
        Player* p = find_random_player(players, Position::AM);
        if (p) return p;
    }
    return players.empty() ? nullptr : &players[0];
}

Player* MatchEngine::find_random_midfielder(std::vector<Player>& players) {
    std::vector<Position> mids = {Position::CM, Position::DM, Position::AM, Position::LW, Position::RW};
    for (auto pos : mids) {
        Player* p = find_random_player(players, pos);
        if (p) return p;
    }
    return players.empty() ? nullptr : &players[0];
}

Player* MatchEngine::find_random_defender(std::vector<Player>& players) {
    std::vector<Position> defs = {Position::CB, Position::LB, Position::RB};
    for (auto pos : defs) {
        Player* p = find_random_player(players, pos);
        if (p) return p;
    }
    return players.empty() ? nullptr : &players[0];
}

double MatchEngine::get_tactical_modifier(const std::string& style, const std::string& aspect) {
    if (aspect == "possession") {
        if (style == "possession") return 1.25;
        if (style == "counter") return 0.85;
        if (style == "direct") return 0.90;
        if (style == "wing_play") return 1.05;
        return 1.0;
    }
    if (aspect == "attack") {
        if (style == "attacking") return 1.20;
        if (style == "counter") return 1.10;
        if (style == "defensive") return 0.85;
        if (style == "wing_play") return 1.15;
        return 1.0;
    }
    if (aspect == "defense") {
        if (style == "defensive") return 1.25;
        if (style == "pressing") return 1.15;
        if (style == "attacking") return 0.85;
        if (style == "counter") return 1.10;
        return 1.0;
    }
    if (aspect == "pressing") {
        if (style == "pressing") return 1.30;
        if (style == "defensive") return 1.10;
        if (style == "possession") return 0.95;
        return 1.0;
    }
    return 1.0;
}

int MatchEngine::get_pace_factor(const Team& team) {
    auto xi = const_cast<Team&>(team).get_starting_xi();
    int total_pace = 0;
    for (auto& p : xi) total_pace += p.pace;
    return total_pace / static_cast<int>(xi.size());
}

MatchResult MatchEngine::simulate_match(Team& home_team, Team& away_team) {
    MatchResult result;
    std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
    std::uniform_int_distribution<int> minute_dist(1, 3);

    std::vector<Player> home_xi = home_team.get_starting_xi();
    std::vector<Player> away_xi = away_team.get_starting_xi();

    double home_possession = calculate_possession(home_team, away_team);
    result.home_possession = home_possession;
    result.away_possession = 100.0 - home_possession;

    double home_attack = calculate_attack_strength(home_team, home_possession);
    double away_attack = calculate_attack_strength(away_team, 100.0 - home_possession);
    double home_defense = calculate_defense_strength(home_team);
    double away_defense = calculate_defense_strength(away_team);

    // Commentary in Russian
    std::string home_name = home_team.name;
    std::string away_name = away_team.name;

    result.commentary_log.push_back(
        "Начало матча! " + home_name + " против " + away_name + "."
    );

    if (weather != "clear") {
        std::string weather_desc;
        if (weather == "rain") weather_desc = "идёт дождь";
        else if (weather == "snow") weather_desc = "идёт снег";
        else if (weather == "wind") weather_desc = "сильный ветер";
        else weather_desc = "непогода";
        result.commentary_log.push_back("Погодные условия: " + weather_desc + ".");
    }

    int minute = 0;
    int home_goals = 0;
    int away_goals = 0;
    int home_shots = 0;
    int away_shots = 0;
    int home_shots_on = 0;
    int away_shots_on = 0;
    double home_xg_total = 0.0;
    double away_xg_total = 0.0;

    // Track yellow/red cards per team
    std::map<int, int> home_cards;
    std::map<int, int> away_cards;

    // Substitution slots
    int home_subs = 0;
    int away_subs = 0;

    while (minute < 90) {
        int jump = minute_dist(rng);
        minute += jump;
        if (minute > 90) minute = 90;

        double event_roll = prob_dist(rng);
        bool is_home_event = prob_dist(rng) < (home_possession / 100.0);

        MatchEvent event;
        event.minute = minute;

        // Determine which event happens
        if (event_roll < 0.12) {
            // Shot attempt
            event.event_type = EventType::SHOT;
            if (is_home_event) {
                event.team_id = home_team.id;
                Player* attacker = find_random_attacker(home_xi);
                if (attacker) event.player_name = attacker->name;
                double xg = calculate_xg(home_attack, away_defense, prob_dist(rng) < 0.2 ? 1 : 0);
                home_xg_total += xg;
                event.xg_value = xg;
                home_shots++;

                bool on_target = prob_dist(rng) < 0.45;
                if (on_target) {
                    home_shots_on++;
                    bool scored = prob_dist(rng) < xg;
                    if (scored) {
                        home_goals++;
                        event.event_type = EventType::GOAL;
                        event.detail = home_name + " забивает! Гол!";
                        result.commentary_log.push_back(
                            std::to_string(minute) + "' - ГОЛ! " + event.player_name +
                            " забивает за " + home_name + "! Счёт: " +
                            std::to_string(home_goals) + " - " + std::to_string(away_goals)
                        );
                    } else {
                        event.detail = "Удар в створ, но вратарь спасает!";
                        result.commentary_log.push_back(
                            std::to_string(minute) + "' - " + event.player_name +
                            " бьёт в створ, но вратарь отражает удар!"
                        );
                    }
                } else {
                    event.detail = "Удар мимо ворот";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - " + event.player_name +
                        " пробивает, но мяч уходит мимо ворот."
                    );
                }
            } else {
                event.team_id = away_team.id;
                Player* attacker = find_random_attacker(away_xi);
                if (attacker) event.player_name = attacker->name;
                double xg = calculate_xg(away_attack, home_defense, prob_dist(rng) < 0.2 ? 1 : 0);
                away_xg_total += xg;
                event.xg_value = xg;
                away_shots++;

                bool on_target = prob_dist(rng) < 0.42;
                if (on_target) {
                    away_shots_on++;
                    bool scored = prob_dist(rng) < xg;
                    if (scored) {
                        away_goals++;
                        event.event_type = EventType::GOAL;
                        event.detail = away_name + " забивает! Гол!";
                        result.commentary_log.push_back(
                            std::to_string(minute) + "' - ГОЛ! " + event.player_name +
                            " забивает за " + away_name + "! Счёт: " +
                            std::to_string(home_goals) + " - " + std::to_string(away_goals)
                        );
                    } else {
                        event.detail = "Удар в створ, но вратарь спасает!";
                        result.commentary_log.push_back(
                            std::to_string(minute) + "' - " + event.player_name +
                            " бьёт в створ, но вратарь отражает!"
                        );
                    }
                } else {
                    event.detail = "Удар мимо ворот";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - " + event.player_name +
                        " пробивает, но мяч летит в пустые ворота."
                    );
                }
            }
            result.events.push_back(event);
        } else if (event_roll < 0.16) {
            // Foul
            event.event_type = EventType::FOUL;
            if (is_home_event) {
                event.team_id = away_team.id;
                Player* fouler = find_random_defender(away_xi);
                if (fouler) event.player_name = fouler->name;
                away_cards[fouler ? fouler->id : 0]++;
            } else {
                event.team_id = home_team.id;
                Player* fouler = find_random_defender(home_xi);
                if (fouler) event.player_name = fouler->name;
                home_cards[fouler ? fouler->id : 0]++;
            }
            event.detail = "Нарушение правил";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Фол! " + event.player_name + " нарушает правила."
            );
            result.events.push_back(event);
        } else if (event_roll < 0.19) {
            // Yellow card
            event.event_type = EventType::YELLOW_CARD;
            if (is_home_event) {
                event.team_id = home_team.id;
                Player* player = find_random_player(home_xi, Position::CM);
                if (player) event.player_name = player->name;
            } else {
                event.team_id = away_team.id;
                Player* player = find_random_player(away_xi, Position::CM);
                if (player) event.player_name = player->name;
            }
            event.detail = "Жёлтая карточка";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Жёлтая карточка! " + event.player_name + " получает предупреждение."
            );
            result.events.push_back(event);
        } else if (event_roll < 0.20) {
            // Red card (rare)
            event.event_type = EventType::RED_CARD;
            if (is_home_event) {
                event.team_id = home_team.id;
                Player* player = find_random_player(home_xi, Position::CM);
                if (player) event.player_name = player->name;
            } else {
                event.team_id = away_team.id;
                Player* player = find_random_player(away_xi, Position::CM);
                if (player) event.player_name = player->name;
            }
            event.detail = "Красная карточка - удаление!";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Красная карточка! " + event.player_name + " удалён с поля!"
            );
            result.events.push_back(event);
        } else if (event_roll < 0.22) {
            // Corner
            event.event_type = EventType::CORNER;
            if (is_home_event) {
                event.team_id = home_team.id;
                Player* player = find_random_midfielder(home_xi);
                if (player) event.player_name = player->name;
            } else {
                event.team_id = away_team.id;
                Player* player = find_random_midfielder(away_xi);
                if (player) event.player_name = player->name;
            }
            event.detail = "Угловой удар";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Угловой! " + event.player_name + " навешивает в штрафную."
            );
            result.events.push_back(event);
        } else if (event_roll < 0.235) {
            // Offside
            event.event_type = EventType::OFFSIDE;
            if (is_home_event) {
                event.team_id = home_team.id;
                Player* player = find_random_attacker(home_xi);
                if (player) event.player_name = player->name;
            } else {
                event.team_id = away_team.id;
                Player* player = find_random_attacker(away_xi);
                if (player) event.player_name = player->name;
            }
            event.detail = "Оффсайд";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Оффсайд! " + event.player_name + " находился за последним защитником."
            );
            result.events.push_back(event);
        } else if (event_roll < 0.245) {
            // Injury
            event.event_type = EventType::INJURY;
            if (is_home_event && home_subs < 3) {
                event.team_id = home_team.id;
                Player* player = find_random_player(home_xi, Position::CM);
                if (player) {
                    event.player_name = player->name;
                    player->fatigue = 100;
                }
                home_subs++;
            } else if (!is_home_event && away_subs < 3) {
                event.team_id = away_team.id;
                Player* player = find_random_player(away_xi, Position::CM);
                if (player) {
                    event.player_name = player->name;
                    player->fatigue = 100;
                }
                away_subs++;
            } else {
                continue;
            }
            event.detail = "Травма игрока";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - " + event.player_name + " получает травму и заменяется!"
            );
            result.events.push_back(event);
        } else if (event_roll < 0.255) {
            // Substitution
            event.event_type = EventType::SUBSTITUTION;
            if (is_home_event && home_subs < 3) {
                event.team_id = home_team.id;
                Player* player = find_random_player(home_xi, Position::CM);
                if (player) event.player_name = player->name;
                home_subs++;
            } else if (!is_home_event && away_subs < 3) {
                event.team_id = away_team.id;
                Player* player = find_random_player(away_xi, Position::CM);
                if (player) event.player_name = player->name;
                away_subs++;
            } else {
                continue;
            }
            event.detail = "Замена";
            result.commentary_log.push_back(
                std::to_string(minute) + "' - Замена! " + event.player_name + " покидает поле."
            );
            result.events.push_back(event);
        } else if (event_roll < 0.260) {
            // Penalty (very rare)
            event.event_type = EventType::PENALTY;
            bool home_pen = prob_dist(rng) < 0.5;
            if (home_pen) {
                event.team_id = home_team.id;
                Player* pen_taker = find_random_attacker(home_xi);
                if (pen_taker) event.player_name = pen_taker->name;
                double xg = 0.76;
                home_xg_total += xg;
                event.xg_value = xg;
                bool scored = prob_dist(rng) < xg;
                if (scored) {
                    home_goals++;
                    event.event_type = EventType::GOAL;
                    event.detail = "Гол с пенальти!";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - ПЕНАЛЬТИ! " + event.player_name +
                        " забивает с одиннадцатиметровой отметки! " +
                        std::to_string(home_goals) + " - " + std::to_string(away_goals)
                    );
                } else {
                    event.detail = "Пенальти промахнут!";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - ПЕНАЛЬТИ! " + event.player_name +
                        " промахивается! Вратарь отбивает!"
                    );
                }
            } else {
                event.team_id = away_team.id;
                Player* pen_taker = find_random_attacker(away_xi);
                if (pen_taker) event.player_name = pen_taker->name;
                double xg = 0.76;
                away_xg_total += xg;
                event.xg_value = xg;
                bool scored = prob_dist(rng) < xg;
                if (scored) {
                    away_goals++;
                    event.event_type = EventType::GOAL;
                    event.detail = "Гол с пенальти!";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - ПЕНАЛЬТИ! " + event.player_name +
                        " забивает! " + std::to_string(home_goals) + " - " + std::to_string(away_goals)
                    );
                } else {
                    event.detail = "Пенальти промахнут!";
                    result.commentary_log.push_back(
                        std::to_string(minute) + "' - ПЕНАЛЬТИ! " + event.player_name +
                        " промахивается!"
                    );
                }
            }
            result.events.push_back(event);
        }
        // VAR check events (very rare, attached to other events)
        else if (event_roll < 0.263) {
            event.event_type = EventType::VAR;
            event.team_id = 0;
            event.detail = "Проверка VAR";
            bool var_confirm = prob_dist(rng) < 0.4;
            if (var_confirm) {
                result.commentary_log.push_back(
                    std::to_string(minute) + "' - VAR проверяет решение. Решение подтверждено!"
                );
            } else {
                result.commentary_log.push_back(
                    std::to_string(minute) + "' - VAR проверяет решение. Решение отменено!"
                );
            }
            result.events.push_back(event);
        }

        if (minute >= 90) break;
    }

    // Half-time commentary
    if (home_goals != 0 || away_goals != 0) {
        result.commentary_log.push_back(
            "Перерыв / Конец матча. Счёт: " + std::to_string(home_goals) +
            " - " + std::to_string(away_goals)
        );
    }

    result.home_goals = home_goals;
    result.away_goals = away_goals;
    result.home_shots = home_shots;
    result.away_shots = away_shots;
    result.home_shots_on_target = home_shots_on;
    result.away_shots_on_target = away_shots_on;
    result.home_xg = home_xg_total;
    result.away_xg = away_xg_total;

    result.man_of_the_match = pick_motm(result, home_xi, away_xi);
    result.match_summary = generate_match_summary(result, home_name, away_name);

    // Apply form changes to players based on result
    int home_result_sign = 0;
    if (home_goals > away_goals) home_result_sign = 1;
    else if (home_goals < away_goals) home_result_sign = -1;

    for (auto& p : home_xi) {
        p.form = std::max(1, std::min(100, p.form + home_result_sign * 5));
        p.fatigue = std::min(100, p.fatigue + 15);
        p.morale = std::max(1, std::min(100, p.morale + home_result_sign * 3));
    }
    for (auto& p : away_xi) {
        p.form = std::max(1, std::min(100, p.form - home_result_sign * 5));
        p.fatigue = std::min(100, p.fatigue + 15);
        p.morale = std::max(1, std::min(100, p.morale - home_result_sign * 3));
    }

    // Write back to original teams
    for (auto& p : home_xi) {
        for (auto& tp : home_team.players) {
            if (tp.id == p.id) { tp = p; break; }
        }
    }
    for (auto& p : away_xi) {
        for (auto& tp : away_team.players) {
            if (tp.id == p.id) { tp = p; break; }
        }
    }

    return result;
}

std::string MatchEngine::generate_commentary(const MatchEvent& event, const std::string& /*home_name*/, const std::string& /*away_name*/) {
    return event.detail;
}

std::string MatchEngine::generate_match_summary(const MatchResult& result, const std::string& home_name, const std::string& away_name) {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(1);
    ss << home_name << " " << result.home_goals << " - " << result.away_goals << " " << away_name << "\n";
    ss << "Владение мячом: " << result.home_possession << "% - " << result.away_possession << "%\n";
    ss << "Удары: " << result.home_shots << " - " << result.away_shots << "\n";
    ss << "Удары в створ: " << result.home_shots_on_target << " - " << result.away_shots_on_target << "\n";
    ss << "xG: " << result.home_xg << " - " << result.away_xg << "\n";
    ss << "Лучший игрок: " << result.man_of_the_match;
    return ss.str();
}

std::string MatchEngine::pick_motm(const MatchResult& result, const std::vector<Player>& home_xi, const std::vector<Player>& away_xi) {
    double best_rating = -1;
    std::string best_name = "Неизвестный";

    // Goal scorers get bonus
    std::map<std::string, int> goals;
    for (auto& e : result.events) {
        if (e.event_type == EventType::GOAL) goals[e.player_name]++;
    }

    auto check_player = [&](const Player& p) {
        double rating = p.overall_rating * 0.4 + p.form * 0.3;
        if (goals.count(p.name)) rating += goals[p.name] * 15.0;
        if (p.position == Position::GK) {
            rating += result.home_shots_on_target + result.away_shots_on_target;
        }
        if (rating > best_rating) {
            best_rating = rating;
            best_name = p.name;
        }
    };

    for (auto& p : home_xi) check_player(p);
    for (auto& p : away_xi) check_player(p);

    return best_name;
}
