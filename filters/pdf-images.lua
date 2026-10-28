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
  function Header(header)
    if header.identifier == 'title' then return {} end
    if header.classes:includes('appendix-section') then
      return {pandoc.RawBlock('latex', '\\appendix\\Needspace{14\\baselineskip}'), header}
    end
    if header.level <= 2 then
      return {pandoc.RawBlock('latex', '\\Needspace{14\\baselineskip}'), header}
    end
  end
  function Div(div)
    if div.classes:includes('title-only') then return {} end
    if div.classes:includes('question') then
      local result={pandoc.RawBlock('latex','\\begin{minipage}{\\linewidth}')}
      for _,block in ipairs(div.content) do result[#result+1]=block end
      return result
    elseif div.classes:includes('answer') then
      local result={}
      for _,block in ipairs(div.content) do result[#result+1]=block end
      result[#result+1]=pandoc.RawBlock('latex','\\end{minipage}\\par\\medskip')
      return result
    end
  end
end
