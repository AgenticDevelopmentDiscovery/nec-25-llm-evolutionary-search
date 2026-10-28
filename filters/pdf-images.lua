-- Portable raster companions; the HTML site retains the original vector SVGs.
if FORMAT:match('latex') or FORMAT:match('beamer') then
  function Image(image)
    image.src = image.src:gsub('%.svg$', '.png')
    if FORMAT:match('latex') and (image.src:match('classroom%-partition') or image.src:match('signed%-four%-vertex')) then
      image.attributes.width = '40%'
    end
    return image
  end
end
if FORMAT:match('latex') then
  local minipage_open = false
  local function close_minipage()
    minipage_open=false
    return pandoc.RawBlock('latex','\\end{minipage}\\par\\medskip')
  end
  function Header(header)
    local result={}
    if header.level<=2 and minipage_open then result[#result+1]=close_minipage() end
    if header.identifier == 'title' then return result end
    if header.classes:includes('appendix-section') then
      result[#result+1]=pandoc.RawBlock('latex','\\appendix\\Needspace{14\\baselineskip}')
    elseif header.level<=2 then
      result[#result+1]=pandoc.RawBlock('latex','\\Needspace{14\\baselineskip}')
    end
    result[#result+1]=header
    return result
  end
  function Div(div)
    if div.classes:includes('title-only') then return {} end
    if div.classes:includes('notes') then
      if minipage_open then return {close_minipage(),div} end
    elseif div.classes:includes('question') or div.classes:includes('block') or div.classes:includes('answer') then
      local result={}
      if not minipage_open then
        result[#result+1]=pandoc.RawBlock('latex','\\begin{minipage}{\\linewidth}')
        minipage_open=true
      end
      for _,block in ipairs(div.content) do result[#result+1]=block end
      if div.classes:includes('answer') then result[#result+1]=close_minipage() end
      return result
    end
  end
  function Pandoc(doc)
    if minipage_open then doc.blocks:insert(close_minipage()) end
    return doc
  end
end
