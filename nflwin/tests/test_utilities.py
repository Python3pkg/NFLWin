

import nfldb
import numpy as np
import pandas as pd
import pytest

import nflwin.utilities as utils

class TestGetNFLDBPlayData(object):
    """Testing the ability to get play data from nfldb."""

    #TODO (AndrewRook): Need to test if the sql query actually works

    def setup_method(self, method):
        self.test_df = pd.DataFrame({
                'gsis_id': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                'drive_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'play_id': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                'time': ["(Q1,0)", "(Q1,152)", "(Q1,354)", "(Q1,354)", "(Q2,0)",
                         "(OT,840)", "(OT,840)", "(OT2,875)", "(OT3,900)", "(OT,900)"],
                'offense_team': ["HOU", "KC", "KC", "HOU", "HOU", "UNK", "DEN", "DEN", "CAR", "UNK"],
                'yardline': ["(-15)", "(35)", "(-15)", "(-30)", "(-26)",
                             None, "(48)", "(-15)", "(-18)", None],
                'down': [np.nan, np.nan, np.nan, 1.0, 2.0, np.nan, 1.0, np.nan, 1.0, np.nan],
                'yards_to_go': [0, 0, 0, 10, 6, 0, 2, 0, 10, 0],
                'offense_play_points': [0, 1, 0, 0, 0, 0, 6, 0, 0, 0],
                'defense_play_points': [6, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'home_team': ["HOU", "HOU", "HOU", "HOU", "HOU", "DEN", "DEN", "DEN", "DEN", "DEN"],
                'away_team': ["KC", "KC", "KC", "KC", "KC", "CAR", "CAR", "CAR", "CAR", "CAR"],
                'offense_won': [False, False, False, False, False, True, True, True, True, True]
                })
        
    def test_standard_play_mock(self,monkeypatch):
        def mockreturn_engine():
            return True
        def mockreturn_query_string(season_years, season_types):
            return True
        def mockreturn_read_sql(sql_string, engine):
            return self.test_df
        monkeypatch.setattr(utils, 'connect_nfldb', mockreturn_engine)
        monkeypatch.setattr(utils, '_make_nfldb_query_string', mockreturn_query_string)
        monkeypatch.setattr(pd, 'read_sql', mockreturn_read_sql)

        expected_df = pd.DataFrame({
                'gsis_id': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                'drive_id': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'play_id': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
                'seconds_elapsed': [0.0, 152.0, 354.0, 354.0, 0.0,
                         840.0, 840.0, 875.0, 900.0, 900.0],
                'offense_team': ["HOU", "KC", "KC", "HOU", "HOU", "UNK", "DEN", "DEN", "CAR", "UNK"],
                'yardline': [-15, 35, -15, -30, -26,
                             np.nan, 48, -15, -18, np.nan],
                'down': [0, 0, 0, 1, 2, 0, 1, 0, 1, 0],
                'yards_to_go': [0, 0, 0, 10, 6, 0, 2, 0, 10, 0],
                'home_team': ["HOU", "HOU", "HOU", "HOU", "HOU", "DEN", "DEN", "DEN", "DEN", "DEN"],
                'away_team': ["KC", "KC", "KC", "KC", "KC", "CAR", "CAR", "CAR", "CAR", "CAR"],
                'offense_won': [False, False, False, False, False, True, True, True, True, True],
                'quarter': ["Q1", "Q1", "Q1", "Q1", "Q2", "OT", "OT", "OT2", "OT3", "OT"],
                'curr_home_score': [0, 0, 0, 0, 0, 0, 0, 7, 7, 7],
                'curr_away_score': [0, 6, 7, 7, 7, 0, 0, 0, 0, 0]
                })
        expected_df['down'] = expected_df['down'].astype(np.int8)
        
        pd.util.testing.assert_frame_equal(utils.get_nfldb_play_data().sort_index(axis=1),
                                           expected_df.sort_index(axis=1))

    @pytest.mark.requires_db
    def test_2015_playoffs_query(self):
        queried_df = utils.get_nfldb_play_data(season_years=[2015], season_types=["Postseason"])
        expected_df = pd.DataFrame({
            'gsis_id': ['2016010900', '2016010900', '2016010900', '2016010900', '2016010900'],
            'drive_id': [1, 1, 2, 2, 2],
            'play_id': [36, 54, 70, 88, 109],
            'seconds_elapsed': [0., 11., 11., 11., 45.],
            'offense_team': ['HOU', 'KC', 'KC', 'HOU', 'HOU'],
            'yardline': [-15., 35, -15, -30, -26],
            'down': [0, 0, 0, 1, 2],
            'yards_to_go': [0, 0, 0, 10, 6],
            'home_team': ['HOU', 'HOU', 'HOU', 'HOU', 'HOU'],
            'away_team': ['KC', 'KC', 'KC', 'KC', 'KC'],
            'offense_won': [False, True, True, False, False],
            'quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q1'],
            'curr_home_score': [0, 0, 0, 0, 0],
            'curr_away_score': [0, 6, 7, 7, 7]
            })
        expected_df['down'] = expected_df['down'].astype(np.int8)
        pd.util.testing.assert_frame_equal(queried_df[:5].sort_index(axis=1),
                                           expected_df.sort_index(axis=1), check_column_type=False)

    @pytest.mark.requires_db
    def test_2009_regular_season_query(self):
        queried_df = utils.get_nfldb_play_data(season_years=[2009], season_types=["Regular"])
        expected_df = pd.DataFrame({
            'gsis_id': ['2009091000', '2009091000', '2009091000', '2009091000', '2009091000'],
            'drive_id': [1, 1, 1, 1, 1],
            'play_id': [46, 68, 92, 113, 139],
            'seconds_elapsed': [0., 7, 44, 85, 93],
            'offense_team': ['TEN', 'PIT', 'PIT', 'PIT', 'PIT'],
            'yardline': [-20., -8, -3, -6, -6],
            'down': [0, 1, 2, 3, 4],
            'yards_to_go': [0, 10, 5, 8, 8],
            'home_team': ['PIT', 'PIT', 'PIT', 'PIT', 'PIT'],
            'away_team': ['TEN', 'TEN', 'TEN', 'TEN', 'TEN'],
            'offense_won': [False, True, True, True, True],
            'quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q1'],
            'curr_home_score': [0, 0, 0, 0, 0],
            'curr_away_score': [0, 0, 0, 0, 0]
            })
        expected_df['down'] = expected_df['down'].astype(np.int8)
        pd.util.testing.assert_frame_equal(queried_df[:5].sort_index(axis=1),
                                           expected_df.sort_index(axis=1), check_column_type=False)


class TestConnectNFLDB(object):
    """testing the connect_nfldb function"""
    def setup_method(self, method):
        self.curr_config_home = nfldb.db._config_home
        
    def teardown_method(self, method):
        nfldb.db._config_home = self.curr_config_home

    def test_no_config_error(self):
        nfldb.db._config_home = "/boogaboogabooga"

        with pytest.raises(IOError):
            utils.connect_nfldb()

    @pytest.mark.requires_db
    def test_engine_works(self):
        engine = utils.connect_nfldb()
        test_query = ("SELECT play.description "
                      "from play "
                      "WHERE play.gsis_id = '2009080950' AND play.play_id=721;")
        
        plays_df = pd.read_sql(test_query, engine)
        
        assert (plays_df.iloc[0]['description'] ==
                '(6:55) L.White left guard for 3 yards, TOUCHDOWN.')

class TestMakeNFLDBQueryString(object):
    """testing the _make_nfldb_query_string function"""
    
    def test_no_args(self):
        expected_string = ("SELECT play.gsis_id, play.drive_id, "
                           "play.play_id, play.time, play.pos_team AS offense_team, "
                           "play.yardline, play.down, play.yards_to_go, "
                           "GREATEST("
                           "(agg_play.fumbles_rec_tds * 6), "
                           "(agg_play.kicking_rec_tds * 6), "
                           "(agg_play.passing_tds * 6), "
                           "(agg_play.receiving_tds * 6), "
                           "(agg_play.rushing_tds * 6), "
                           "(agg_play.kicking_xpmade * 1), "
                           "(agg_play.passing_twoptm * 2), "
                           "(agg_play.receiving_twoptm * 2), "
                           "(agg_play.rushing_twoptm * 2), "
                           "(agg_play.kicking_fgm * 3)) AS offense_play_points, "
                           "GREATEST("
                           "(agg_play.defense_frec_tds * 6), "
                           "(agg_play.defense_int_tds * 6), "
                           "(agg_play.defense_misc_tds * 6), "
                           "(agg_play.kickret_tds * 6), "
                           "(agg_play.puntret_tds * 6), "
                           "(agg_play.defense_safe * 2)) AS defense_play_points, "
                           "game.home_team, game.away_team, "
                           "((game.home_score > game.away_score AND play.pos_team = game.home_team) OR "
                           "(game.away_score > game.home_score AND play.pos_team = game.away_team))"
                           " AS offense_won "
                           "FROM play INNER JOIN agg_play "
                           "ON play.gsis_id = agg_play.gsis_id "
                           "AND play.drive_id = agg_play.drive_id "
                           "AND play.play_id = agg_play.play_id "
                           "INNER JOIN game on play.gsis_id = game.gsis_id "
                           "WHERE game.home_score != game.away_score AND game.finished = TRUE "
                           "AND play.pos_team != 'UNK' "
                           "AND (play.time).phase not in ('Pregame', 'Half', 'Final') "
                           "ORDER BY play.gsis_id, play.drive_id, play.play_id;")
        assert expected_string == utils._make_nfldb_query_string()

    def test_single_year(self):
        """Test that adding a single year constraint works"""
        expected_substring = ("WHERE game.home_score != game.away_score "
                              "AND game.finished = TRUE "
                              "AND play.pos_team != 'UNK' "
                              "AND (play.time).phase not in ('Pregame', 'Half', 'Final') "
                              "AND game.season_year = 2013")
        assert expected_substring in utils._make_nfldb_query_string(season_years=[2013])

    def test_single_season_type(self):
        """Test that adding a single season type constraint works"""
        expected_substring = ("WHERE game.home_score != game.away_score "
                              "AND game.finished = TRUE "
                              "AND play.pos_team != 'UNK' "
                              "AND (play.time).phase not in ('Pregame', 'Half', 'Final') "
                              "AND game.season_type = 'Regular'")
        assert expected_substring in utils._make_nfldb_query_string(season_types=["Regular"])

    def test_multiple_year(self):
        """Test that adding a multiple year constraint works"""
        expected_substring = ("WHERE game.home_score != game.away_score "
                              "AND game.finished = TRUE "
                              "AND play.pos_team != 'UNK' "
                              "AND (play.time).phase not in ('Pregame', 'Half', 'Final') "
                              "AND game.season_year in (2013,2010)")
        assert expected_substring in utils._make_nfldb_query_string(season_years=[2013, 2010])

    def test_multiple_season_type(self):
        """Test that adding a single season type constraint works"""
        expected_substring = ("WHERE game.home_score != game.away_score "
                              "AND game.finished = TRUE "
                              "AND play.pos_team != 'UNK' "
                              "AND (play.time).phase not in ('Pregame', 'Half', 'Final') "
                              "AND game.season_type in ('Regular','Postseason'")
        assert expected_substring in utils._make_nfldb_query_string(season_types=["Regular", "Postseason"])

            
class TestAggregateNFLDBScores(object):
    """Testing the _aggregate_nfldb_scores function"""

    def test_single_game_offense_points(self):
        input_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'KC', 'NE', 'NE', 'NE', 'NE'],
                                 'home_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'away_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE'],
                                 'offense_play_points': [0, 0, 3, 0, 0, 6, 1, 0],
                                 'defense_play_points': [0, 0, 0, 0, 0, 0, 0, 0]
                                 })
        expected_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'KC', 'NE', 'NE', 'NE', 'NE'],
                                 'home_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'away_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE']
                                 })
        #Have to append the score columns manually:
        expected_df[['curr_home_score', 'curr_away_score']] = pd.DataFrame([(0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (3, 0),
                                                                            (3, 0),
                                                                            (3, 0),
                                                                            (3, 6),
                                                                            (3, 7),])
        
        input_df = utils._aggregate_nfldb_scores(input_df)
        pd.util.testing.assert_frame_equal(input_df, expected_df)

    def test_single_game_defense_points(self):
        input_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'KC', 'NE', 'NE', 'NE', 'NE'],
                                 'away_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'home_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE'],
                                 'offense_play_points': [0, 0, 3, 0, 0, 6, 1, 0],
                                 'defense_play_points': [0, 0, 0, 0, 0, 0, 0, 0]
                                 })
        expected_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'KC', 'NE', 'NE', 'NE', 'NE'],
                                 'away_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'home_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE']
                                 })
        #Have to append the score columns manually:
        expected_df[['curr_home_score', 'curr_away_score']] = pd.DataFrame([(0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 3),
                                                                            (0, 3),
                                                                            (0, 3),
                                                                            (6, 3),
                                                                            (7, 3),])
        
        input_df = utils._aggregate_nfldb_scores(input_df)
        pd.util.testing.assert_frame_equal(input_df, expected_df)

    def test_multiple_games(self):
        input_df = pd.DataFrame({'gsis_id': [0, 0, 0, 1, 1, 1, 1, 1],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'NYJ', 'NE', 'NE', 'NE', 'NE'],
                                 'home_team': ['KC', 'KC', 'KC', 'NYJ', 'NYJ', 'NYJ', 'NYJ', 'NYJ'],
                                 'away_team': ['DEN', 'DEN', 'DEN', 'NE', 'NE', 'NE', 'NE', 'NE'],
                                 'offense_play_points': [0, 0, 3, 0, 0, 6, 1, 0],
                                 'defense_play_points': [0, 0, 0, 0, 0, 0, 0, 0]
                                 })
        expected_df = pd.DataFrame({'gsis_id': [0, 0, 0, 1, 1, 1, 1, 1],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'NYJ', 'NE', 'NE', 'NE', 'NE'],
                                 'home_team': ['KC', 'KC', 'KC', 'NYJ', 'NYJ', 'NYJ', 'NYJ', 'NYJ'],
                                 'away_team': ['DEN', 'DEN', 'DEN', 'NE', 'NE', 'NE', 'NE', 'NE']
                                 })
        #Have to append the score columns manually:
        expected_df[['curr_home_score', 'curr_away_score']] = pd.DataFrame([(0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 6),
                                                                            (0, 7),])
        
        input_df = utils._aggregate_nfldb_scores(input_df)
        pd.util.testing.assert_frame_equal(input_df, expected_df)

    def test_missing_xp(self):
        input_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'NE', 'KC', 'KC', 'KC', 'KC'],
                                 'home_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'away_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE'],
                                 'offense_play_points': [0, 0, 0, 0, 0, 0, 6, 0],
                                 'defense_play_points': [0, 0, 6, 0, 0, 0, 0, 0]
                                 })
        expected_df = pd.DataFrame({'gsis_id': [0, 0, 0, 0, 0, 0, 0, 0],
                                 'yardline': [0, 0, 0, -15, 0, 0, 0, -15],
                                 'offense_team': ['KC', 'KC', 'KC', 'NE', 'KC', 'KC', 'KC', 'KC'],
                                 'home_team': ['KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC', 'KC'],
                                 'away_team': ['NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE', 'NE']
                                 })
        #Have to append the score columns manually:
        expected_df[['curr_home_score', 'curr_away_score']] = pd.DataFrame([(0, 0),
                                                                            (0, 0),
                                                                            (0, 0),
                                                                            (0, 7),
                                                                            (0, 7),
                                                                            (0, 7),
                                                                            (0, 7),
                                                                            (7, 7),])
        
        input_df = utils._aggregate_nfldb_scores(input_df)
        pd.util.testing.assert_frame_equal(input_df, expected_df)


    

        
