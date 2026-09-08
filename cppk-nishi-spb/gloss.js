(function () {
  var TEXTS = {
    utm: "Права Гостехнадзора на погрузчик, трактор и другую самоходку. Это не права на легковую машину.",
    dopog: "Свидетельство, без которого нельзя возить опасный груз. Короткий курс и экзамен комиссии.",
    bdd: "Курсы для тех, кто в организации отвечает за водителей и машины. Не экзамен в ГИБДД.",
    ot: "Обучение правилам безопасной работы. Это не права и не ДОПОГ.",
    gosteh: "Инспекция. Принимает экзамен на самоходку: погрузчик, трактор, каток.",
    egrul: "Реестр юрлиц налоговой. Оттуда название, директор и филиалы.",
    fz223: "Как госучреждение покупает услуги. Рекламу с личной карты так не оплатить.",
    pp805: "С 31 августа 2026 практику первой помощи и работу со средствами защиты нельзя провести только через интернет.",
    siz: "Каска, перчатки, огнетушитель — то, что надевают руками, не только читают.",
    dpo: "Курсы для тех, у кого уже есть профессия или диплом.",
    pk: "Короткий курс для тех, кто уже работает по этой теме.",
    fgaou: "Форма нашего учреждения: федеральное государственное автономное.",
    fku: "Федеральное казённое учреждение. Заказчик вроде управления дороги, не розничный ученик.",
    gbu: "Городское бюджетное учреждение: двор, уборка, техника района.",
    rostrans: "Служба, которая ведёт реестр центров ДОПОГ.",
    tam: "Весь рынок обучения водителей в городе. Это не наши деньги.",
    sam: "Та часть рынка, которую мы умеем продавать.",
    som: "Реальный потолок одной площадки, не всего города.",
    dot: "Учёба через интернет, без класса.",
    uprdor: "Управление федеральных дорог. Заказчик, не автошкола.",
    cpl: "Сколько в среднем стоит одна заявка из рекламы."
  };

  var TERMS = [
    { key: "pp805", re: /постановление Правительства № 805|постановление № 805|ПП 805/g },
    { key: "fgaou", re: /ФГАОУ ДПО/g },
    { key: "fz223", re: /223-ФЗ/g },
    { key: "rostrans", re: /Ространснадзор(?:а|у)?/g },
    { key: "gosteh", re: /Гостехнадзор(?:а|е|у)?/g },
    { key: "ot", re: /охрана труда|охраны труда|охрану труда|охраной труда|Охрана труда|дистант ОТ/g },
    { key: "pk", re: /ПК дорожников|очный ПК|локальный ПК|отраслевой ПК/g },
    { key: "utm", re: /УТМ/g },
    { key: "dopog", re: /ДОПОГ/g },
    { key: "bdd", re: /БДД/g },
    { key: "siz", re: /СИЗ/g },
    { key: "egrul", re: /ЕГРЮЛ/g },
    { key: "fku", re: /ФКУ/g },
    { key: "gbu", re: /ГБУ/g },
    { key: "tam", re: /TAM/g },
    { key: "sam", re: /SAM/g },
    { key: "som", re: /SOM/g },
    { key: "cpl", re: /CPL/g },
    { key: "dot", re: /ДОТ/g },
    { key: "dpo", re: /ДПО/g },
    { key: "uprdor", re: /Упрдор/g }
  ];

  var used = {};
  var openBtn = null;
  var pop = null;

  function skipped(node) {
    var el = node.parentElement;
    if (!el) return true;
    return Boolean(el.closest("nav, .brand, script, style, noscript, .gloss, .mock, .bubble, code, .hub-row, .hub-dash"));
  }

  function definedHere(text, match, index) {
    var after = text.slice(index + match.length, index + match.length + 10);
    return /^\s*[—–\-]\s/.test(after) || /^\s*\(/.test(after);
  }

  function wrap(textNode, start, length, key, label) {
    var text = textNode.nodeValue;
    var parent = textNode.parentNode;
    var span = document.createElement("span");
    span.className = "gloss";
    span.tabIndex = 0;
    span.setAttribute("role", "button");
    span.setAttribute("aria-expanded", "false");
    span.dataset.gloss = key;
    span.textContent = label;
    if (start > 0) parent.insertBefore(document.createTextNode(text.slice(0, start)), textNode);
    parent.insertBefore(span, textNode);
    var rest = text.slice(start + length);
    if (rest) textNode.nodeValue = rest;
    else parent.removeChild(textNode);
    return rest ? textNode : null;
  }

  function process(textNode) {
    if (!textNode || !textNode.parentNode || skipped(textNode)) return;
    var text = textNode.nodeValue;
    if (!text) return;
    var best = null;
    for (var i = 0; i < TERMS.length; i += 1) {
      var term = TERMS[i];
      if (used[term.key]) continue;
      term.re.lastIndex = 0;
      var match = term.re.exec(text);
      if (!match) continue;
      if (definedHere(text, match[0], match.index)) continue;
      if (!best || match.index < best.index) {
        best = { key: term.key, index: match.index, length: match[0].length, label: match[0] };
      }
    }
    if (!best) return;
    used[best.key] = true;
    var rest = wrap(textNode, best.index, best.length, best.key, best.label);
    if (rest) process(rest);
  }

  function closePop() {
    if (pop) pop.hidden = true;
    if (openBtn) {
      openBtn.setAttribute("aria-expanded", "false");
      openBtn = null;
    }
  }

  function placePop(btn) {
    var box = btn.getBoundingClientRect();
    var width = Math.min(280, window.innerWidth - 24);
    var left = box.left + window.scrollX;
    if (left + width > window.scrollX + window.innerWidth - 12) {
      left = window.scrollX + window.innerWidth - width - 12;
    }
    if (left < window.scrollX + 12) left = window.scrollX + 12;
    pop.style.width = width + "px";
    pop.style.left = left + "px";
    pop.hidden = false;
    var popH = pop.offsetHeight;
    var top = box.bottom + window.scrollY + 8;
    if (box.bottom + popH + 16 > window.innerHeight && box.top > popH + 16) {
      top = box.top + window.scrollY - popH - 8;
    }
    pop.style.top = top + "px";
  }

  function openPop(btn) {
    var key = btn.dataset.gloss;
    var text = TEXTS[key];
    if (!text) return;
    if (!pop) {
      pop = document.createElement("div");
      pop.className = "gloss-pop";
      pop.hidden = true;
      document.body.appendChild(pop);
    }
    if (openBtn === btn) {
      closePop();
      return;
    }
    closePop();
    pop.textContent = text;
    openBtn = btn;
    btn.setAttribute("aria-expanded", "true");
    placePop(btn);
  }

  function onActivate(event) {
    var btn = event.target.closest(".gloss");
    if (!btn) return;
    event.preventDefault();
    event.stopPropagation();
    openPop(btn);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        if (skipped(node)) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (var i = 0; i < nodes.length; i += 1) process(nodes[i]);

    document.addEventListener("click", function (event) {
      if (event.target.closest(".gloss")) {
        onActivate(event);
        return;
      }
      if (pop && !event.target.closest(".gloss-pop")) closePop();
    }, true);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closePop();
      if ((event.key === "Enter" || event.key === " ") && event.target.classList.contains("gloss")) {
        onActivate(event);
      }
    });
    window.addEventListener("resize", closePop);
    window.addEventListener("scroll", closePop, { passive: true });
  });
})();
