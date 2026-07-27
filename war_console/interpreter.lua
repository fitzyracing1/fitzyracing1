-- weather.interpreter.lua
function interpret(block)
  local tags = {}
  if tonumber(block.temp) > 30 then table.insert(tags, "@heatwave") end
  if tonumber(block.humidity) > 80 then table.insert(tags, "@sticky") end
  if tonumber(block.precip) > 20 then table.insert(tags, "@flood_warning") end
  return tags
end