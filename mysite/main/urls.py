from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("reports/", views.reports, name="reports"),
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name="logout"),
    path("password_reset/", views.password_reset_request, name="password_reset"),

    path("rocket/", views.rocket, name="rocket"),
    path("payment/", views.payment, name="payment"),
    path('ip_info/', views.info_by_ip, name='ip_info'),

    path('risks_rep/', views.risks_rep, name='risks_rep'),
    path('add_personal_report/', views.add_personal_report, name='add_personal_report'),
    path('add_day_report/', views.add_day_report, name='add_day_report'),
    path('list_risks_rep/', views.ListRisksReport.as_view(), name='list_risks_rep'),
    path('update_risks_rep/<int:pk>', views.UpdateRisksReport.as_view(), name='update_risks_rep'),
    path('list_risks_rep_day/', views.ListRisksReportDay.as_view(), name='list_risks_rep_day'),
    path('update_risks_rep_day/<int:pk>', views.UpdateRisksReportDay.as_view(), name='update_risks_rep_day'),
    path('fd_rep/', views.first_deposit_amount_over_1000, name='fd_rep'),

    path('add_data/', views.AddDataFromTextView.as_view(), name='add_data'),
    path('calls_rep/', views.CallsView.as_view(), name='calls_rep'),
    path('update_calls/<int:pk>', views.UpdateCallView.as_view(), name='update_calls'),
    path('add_crm_data/', views.AddDataFromCRMView.as_view(), name='add_crm_data'),
    path('crm_rep/', views.CRMView.as_view(), name='crm_rep'),
    path('update_crm/<int:pk>', views.UpdateCRMView.as_view(), name='update_crm'),
    path('cc_report/', views.CCReportView.as_view(), name='cc_report'),
    path('appeal/', views.AppealReportView.as_view(), name='appeal'),
    path('appeal_rep/', views.AppealReportListView.as_view(), name='appeal_rep'),
    path('update_appeal/<int:pk>', views.UpdateAppealView.as_view(), name='update_appeal'),
    path('find_calls/', views.FindCalls.as_view(), name='find_calls'),

    path('log_file/', views.view_log_file, name='log_file'),

    path('skks_games/', views.GameListFromSkksView.as_view(), name='skks_games'),
    path('skks_games_test/', views.GameListFromSkksTestView.as_view(), name='skks_games_test'),
    path('site_games/', views.GameListFromSiteView.as_view(), name='site_games'),
    path('disabled_games/', views.GameDisableListView.as_view(), name='disabled_games'),
    path('add_game_disable/', views.AddGameDisableView.as_view(), name='add_game_disable'),
    path('missing_games/', views.MissingGamesListView.as_view(), name='missing_games'),
    path('rounds_rep/', views.no_close_rounds_rep, name='rounds_rep'),
    path('rounds/', views.no_close_rounds_report, name='rounds'),
    path('hold_round/', views.CloseHoldRoundView.as_view(), name='hold_round'),
    path('transaction_cancel/', views.TransactionCancelView.as_view(), name='transaction_cancel'),
    path('create_payout_request/', views.CreatePayoutRequestView.as_view(), name='create_payout_request'),
    path('create_player_in/', views.CreateTransactionPlayerInView.as_view(), name='create_player_in'),
    path('add_game/', views.AddGameToSKKSHostView.as_view(), name='add_game'),
]
