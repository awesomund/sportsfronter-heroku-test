from django.conf.urls import patterns, url

urlpatterns = patterns('management.views',

    url(r'^teams', 'get_teams'),
    url(r'^allteams', 'get_all_teams'),
    url(r'^team/add', 'add_team'),
    url(r'^team/search/(?P<search_term>\w+)', 'team_search'),
    url(r'^team/(?P<team_id>\d+)/mergeplayers', 'merge_players'),
    url(r'^team/(?P<team_id>\d+)/guardian_add_player', 'guardian_add_player'),
    url(r'^team/(?P<team_id>\d+)/guardian_connect_to_player', 'guardian_connect_to_player'),
    url(r'^team/(?P<team_id>\d+)/player/add', 'add_player'),
    url(r'^team/(?P<team_id>\d+)/coach/add/(?P<player_id>\d+)', 'add_player_as_coach'),
    url(r'^team/(?P<team_id>\d+)/coach/add', 'save_coach'),
    url(r'^team/(?P<team_id>\d+)/coach/(?P<coach_id>\d+)', 'get_coach_info'),
    url(r'^team/(?P<team_id>\d+)/coach/remove', 'remove_coach_from_team'),
    url(r'^team/(?P<team_id>\d+)/name', 'get_team_name'),
    url(r'^team/(?P<team_id>\d+)/get_guardian_players_for_team', 'get_guardian_players_for_team'),
    url(r'^team/(?P<team_id>\d+)/join', 'join_team'),
    url(r'^team/(?P<team_id>\d+)', 'get_team'),
    url(r'^team/delete_team', 'delete_team'),
    url(r'^team/change_team_name', 'change_team_name'),
    url(r'^team/getNFFiCalEvent', 'get_nff_ical_events'),

    url(r'^player/(?P<player_id>\d+)/update', 'update_player'),
    url(r'^player/(?P<player_id>\d+)/remove', 'remove_from_team'),
    url(r'^player/(?P<player_id>\d+)', 'get_player_info'),

    url(r'^person/(?P<player_email>\w+[^/]+\w)', 'get_person_from_email'),

    url(r'^get_user_info', 'get_user_info'),
    url(r'^update_user_info', 'update_user_info')
)
