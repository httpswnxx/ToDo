from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class AnonDailyThrottle(AnonRateThrottle):
    scope = 'anon_daily'

class UserDailyThrottle(UserRateThrottle):
    scope = 'user_daily'