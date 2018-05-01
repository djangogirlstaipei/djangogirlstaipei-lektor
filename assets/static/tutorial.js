/* global $ katex */

if (katex) {
    $('span.math').each(function () {
      katex.render(this.textContent, this)
    })
  }
  
  var parseParam = function (query) {
    var obj = {}
    if (!query) {
      return obj
    }
    $.each(query.split('&'), function (i, v) {
      var pair = v.split('=')
      obj[pair[0]] = pair[1]
    })
    return obj
  }

  var detectOS = function () {
    var plat = navigator.platform.toUpperCase()
    if (plat.indexOf('MAC') !== -1) {
      return 'osx'
    } else if (plat.indexOf('WIN') !== -1) {
      return 'windows'
    } else {
      return 'linux'
    }
  }
  
  var switchOS = function (name) {
    var pathParts = document.location.href.split('?')
    var params = parseParam(pathParts[1])
    if (!name) {
      name = params.os ? params.os : detectOS()
    }

    // Show only text code blocks for current OS.
    $('.os').hide().filter('.' + name).show()
  
    // Show fallback in code block collections without variant for current OS.
    $('pre.os.default').each(function () {
      $(this)[$(this).siblings('pre.os.' + name).size() ? 'hide' : 'show']()
    })
  
    // Use the history API to add the OS name to the query string.
    if (window.history && window.history.replaceState) {
      if (params.os !== name) {
        params.os = name
        window.history.replaceState(
          window.history.state,
          document.title,
          pathParts[0] + '?' + $.param(params)
        )
      }
    }

    // Select the corresponding item.
    $('#id_os').val(name)
  }
  
  switchOS(null)
  
  $('#id_os').change(function (e) {
    var name = $(this).val()
    switchOS(name)
  })
