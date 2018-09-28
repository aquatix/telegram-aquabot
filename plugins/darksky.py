import datetime
import logging

import forecastio
import pytz

logger = logging.getLogger(__name__)

EMOJI = {
    'sunrise': '🌅',
    'sunset': '🌇',
    'new-moon': '🌑',
    'waxing-crescent-moon': '🌒',
    'first-quarter-moon': '🌓',
    'waxing-gibbous-moon': '🌔',
    'full-moon': '🌕',
    'waning-gibbous-moon': '🌖',
    'last-quarter-moon': '🌗',
    'waning-crescent-moon': '🌘',
}


def format_sun_and_moon(sun_moon):
    return {
        'message': '{} {}  {}  {} {}'.format(
            EMOJI['sunrise'],
            sun_moon['sunrise'].strftime('%H:%M'),
            EMOJI[sun_moon['moonphase-symbol']],
            EMOJI['sunset'],
            sun_moon['sunset'].strftime('%H:%M')
        )
    }


def get_forecasts(api_key, lat, lng):
    """Gets the current forecast for lat, lng"""
    current_time = datetime.datetime.now()
    forecast = forecastio.load_forecast(api_key, lat, lng, time=current_time)
    result = {}
    for day in forecast.daily().data:
        sunrise = pytz.utc.localize(day.sunriseTime)
        sundown = pytz.utc.localize(day.sunsetTime)
        print('Sun up: {}, sun down: {}, moon phase: {}'.format(sunrise, sundown, day.moonPhase))
    day = forecast.daily().data[0]
    result['sunrise'] = pytz.utc.localize(day.sunriseTime).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    result['sunset'] = pytz.utc.localize(day.sunsetTime).replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    result['moonphase'] = day.moonPhase
    return result


def get_moonphase_name(moonphase):
    """Gets moonphase 'name' for the fraction `moonphase`
    
    0 is full moon
    0.25 is first quarter moon
    0.5 is full moon
    0.75 is last quarter moon

    add -symbol to the name to get the corresponding emoji
    """
    moonphases = {
        'new-moon': (0.0, 0.0),
        'waxing-crescent-moon': (0.01, 0.20),
        'first-quarter-moon': (0.21, 0.30),
        'waxing-gibbous-moon': (0.31, 0.45),
        'full-moon': (0.46, 0.54),
        'waning-gibbous-moon': (0.55, 0.70),
        'last-quarter-moon': (0.71, 0.80),
        'waning-crescent-moon': (0.81, 1.00),
        }

    for phase in moonphases:
        if moonphases[phase][0] <= moonphase <= moonphases[phase][1]:
            return phase


# def get_sun_up_down(


def get_sun_and_moon(settings):
    forecast = get_forecasts(settings.DARKSKY_APIKEY, settings.DARKSKY_LAT, settings.DARKSKY_LON)
    forecast['moonphase-symbol'] = get_moonphase_name(forecast['moonphase'])
    # print(format_sun_and_moon(forecast))
    return format_sun_and_moon(forecast)
