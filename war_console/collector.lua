-- weather.collector.lua
-- Fetches JSON from API, emits symbolic registry block

function collect_weather(api_response)
  return {
    tag = "@weather:Tokyo",
    temp = api_response.main.temp .. "°C",
    humidity = api_response.main.humidity .. "%",
    wind = api_response.wind.speed .. " km/h " .. api_response.wind.deg .. "°",
    precip = (api_response.rain and api_response.rain["1h"] or 0) .. "mm"
  }
end