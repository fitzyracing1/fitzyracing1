-- weather.alerts.lua
function trap_alerts(tags)
  for _,tag in ipairs(tags) do
    if tag == "@flood_warning" then
      print("⚠ Flood risk detected")
    end
  end
end