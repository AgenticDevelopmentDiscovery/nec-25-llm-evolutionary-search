-- Questions, then two blocks, then answers. Notes remain in article/site only.
if FORMAT:match('beamer') then
  local columns_open = false
  local appendix_frame = 0
  function Meta(meta)
    meta.title=nil; meta.subtitle=nil; meta.author=nil; meta.date=nil
    return meta
  end
  function Header(header)
    if header.level==1 then
      return {}
    end
    if header.level==2 and header.classes:includes('appendix') then
      appendix_frame=appendix_frame+1
      local prefix=pandoc.List{pandoc.Str('Appendix'),pandoc.Space(),pandoc.Str('A'..appendix_frame..':'),pandoc.Space()}
      prefix:extend(header.content);header.content=prefix
      return header
    end
  end
  function Div(div)
    if div.identifier=='refs' or div.classes:includes('notes') then return {} end
    if div.classes:includes('visual') then
      local source = pandoc.utils.stringify(div.content)
      local is_partition = false
      local is_architecture = false
      local picture = "classroom-partition"
      div:walk({Image=function(image)
        if image.src:match('classroom%-partition') then is_partition = true end
        if image.src:match('signed%-four%-vertex') then is_partition=true;picture='signed-four-vertex' end
        if image.src:match('architecture%-overview') then is_architecture=true end
      end})
      if is_architecture then
        return pandoc.RawBlock('beamer','\\pause\\begin{center}\\includegraphics[width=\\textwidth]{figures/architecture-overview.png}\\end{center}')
      end
      if is_partition then
        columns_open = true
        return {pandoc.RawBlock('beamer', '\\pause\\begin{columns}[T]\\begin{column}{.35\\textwidth}\\centering\\includegraphics[height=2.8cm]{figures/'..picture..'.png}\\end{column}\\begin{column}{.61\\textwidth}')}
      end
    end
    if div.classes:includes('block') or div.classes:includes('answer') then
      local result={pandoc.RawBlock('beamer','\\pause')}
      if div.classes:includes('answer') and columns_open then
        table.insert(result, 1, pandoc.RawBlock('beamer','\\end{column}\\end{columns}'))
        columns_open = false
      end
      for _,block in ipairs(div.content) do result[#result+1]=block end
      return result
    end
    return div.content
  end
end
