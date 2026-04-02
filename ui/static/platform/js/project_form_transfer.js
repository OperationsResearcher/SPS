/**
 * Micro proje formu — Proje lideri (tek) + üyeler + gözlemciler (süreç paneli ile aynı UX).
 * Gönderim: gizli inputlar (leaders / members / observers); çoklu seçim tarayıcı kısıtına takılmaz.
 */
(function () {
  function toast(kind, msg) {
    if (typeof window.showToast === "function") {
      window.showToast(kind, msg);
      return;
    }
    if (typeof Swal !== "undefined") {
      var icon = kind === "error" ? "error" : kind === "warning" ? "warning" : kind === "success" ? "success" : "info";
      Swal.fire({
        toast: true,
        position: "top-end",
        icon: icon,
        title: msg,
        showConfirmButton: false,
        timer: 2800,
      });
    } else {
      window.alert(msg);
    }
  }

  function parseJsonEl(id) {
    var el = document.getElementById(id);
    if (!el || !el.textContent) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  function sortByLabel(a, b) {
    return (a.label || "").localeCompare(b.label || "", "tr", { sensitivity: "base" });
  }

  function userMap(users) {
    var m = {};
    users.forEach(function (u) {
      m[u.id] = u;
    });
    return m;
  }

  function clearSelect(sel) {
    while (sel.firstChild) sel.removeChild(sel.firstChild);
  }

  function fillSelect(sel, userList) {
    clearSelect(sel);
    userList.slice().sort(sortByLabel).forEach(function (u) {
      sel.appendChild(new Option(u.label, String(u.id)));
    });
  }

  function selectedOptions(sel) {
    return Array.prototype.slice.call(sel.selectedOptions || []);
  }

  function memberIds(memDst) {
    return Array.prototype.map.call(memDst.options, function (o) {
      return parseInt(o.value, 10);
    });
  }

  function removeObserverIfMember(obsDst, uid) {
    Array.prototype.slice.call(obsDst.options).forEach(function (o) {
      if (parseInt(o.value, 10) === uid) obsDst.removeChild(o);
    });
  }

  function rebuildManagerSource(allUsers, mgrSrc, mgrDst) {
    var taken = {};
    Array.prototype.forEach.call(mgrDst.options, function (o) {
      taken[o.value] = true;
    });
    var avail = allUsers.filter(function (u) {
      return !taken[String(u.id)];
    });
    fillSelect(mgrSrc, avail);
  }

  function rebuildMemberSource(allUsers, memSrc, memDst) {
    var taken = {};
    Array.prototype.forEach.call(memDst.options, function (o) {
      taken[o.value] = true;
    });
    var avail = allUsers.filter(function (u) {
      return !taken[String(u.id)];
    });
    fillSelect(memSrc, avail);
  }

  function rebuildObserverSource(allUsers, obsSrc, obsDst, memDst) {
    var inObs = {};
    Array.prototype.forEach.call(obsDst.options, function (o) {
      inObs[o.value] = true;
    });
    var mem = {};
    Array.prototype.forEach.call(memDst.options, function (o) {
      mem[o.value] = true;
    });
    var avail = allUsers.filter(function (u) {
      return !inObs[String(u.id)] && !mem[String(u.id)];
    });
    fillSelect(obsSrc, avail);
  }

  function addFromTo(src, dst, opts) {
    opts = opts || {};
    var max = opts.max || 0;
    var sel = selectedOptions(src);
    if (!sel.length) {
      toast("warning", "Önce soldan seçim yapın.");
      return;
    }
    if (max === 1 && dst.options.length) {
      var first = dst.options[0];
      dst.removeChild(first);
      if (!Array.prototype.some.call(src.options, function (o) { return o.value === first.value; })) {
        src.appendChild(new Option(first.text, first.value));
      }
    }
    sel.forEach(function (opt) {
      if (Array.prototype.some.call(dst.options, function (o) { return o.value === opt.value; })) return;
      dst.appendChild(new Option(opt.text, opt.value));
      src.removeChild(opt);
    });
    if (opts.onAfter) opts.onAfter();
  }

  function removeFromTo(dst, src, onAfter) {
    var sel = selectedOptions(dst);
    if (!sel.length) {
      toast("warning", "Önce sağdan seçim yapın.");
      return;
    }
    sel.forEach(function (opt) {
      dst.removeChild(opt);
      if (!Array.prototype.some.call(src.options, function (o) { return o.value === opt.value; })) {
        src.appendChild(new Option(opt.text, opt.value));
      }
    });
    var arr = Array.prototype.slice.call(src.options);
    arr.sort(function (a, b) {
      return a.text.localeCompare(b.text, "tr", { sensitivity: "base" });
    });
    clearSelect(src);
    arr.forEach(function (o) {
      src.appendChild(o);
    });
    if (onAfter) onAfter();
  }

  function bindFilter(inputId, selectId) {
    var input = document.getElementById(inputId);
    var select = document.getElementById(selectId);
    if (!input || !select) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      Array.prototype.forEach.call(select.options, function (opt) {
        opt.hidden = q.length > 0 && opt.textContent.toLowerCase().indexOf(q) === -1;
      });
    });
  }

  function syncHiddenFromSelect(dst, container, name) {
    container.innerHTML = "";
    Array.prototype.forEach.call(dst.options, function (opt) {
      var inp = document.createElement("input");
      inp.type = "hidden";
      inp.name = name;
      inp.value = opt.value;
      container.appendChild(inp);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("micro-project-form");
    if (!form) return;

    var users = parseJsonEl("micro-proj-form-users");
    var init = parseJsonEl("micro-proj-form-init");
    if (!users || !users.length || !init) return;

    var byId = userMap(users);
    var allUsers = users.slice().sort(sortByLabel);

    var mgrSrc = document.getElementById("micro-proj-mgr-src");
    var mgrDst = document.getElementById("micro-proj-mgr-dst");
    var memSrc = document.getElementById("micro-proj-mem-src");
    var memDst = document.getElementById("micro-proj-mem-dst");
    var obsSrc = document.getElementById("micro-proj-obs-src");
    var obsDst = document.getElementById("micro-proj-obs-dst");
    var hidLeaders = document.getElementById("micro-proj-hidden-leaders");
    var hidMem = document.getElementById("micro-proj-hidden-mem");
    var hidObs = document.getElementById("micro-proj-hidden-obs");

    if (!mgrSrc || !mgrDst || !memSrc || !memDst || !obsSrc || !obsDst || !hidLeaders || !hidMem || !hidObs) return;

    function refreshAllSources() {
      rebuildManagerSource(allUsers, mgrSrc, mgrDst);
      rebuildMemberSource(allUsers, memSrc, memDst);
      rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
    }

    function initDestFromIds(dst, ids) {
      clearSelect(dst);
      ids.forEach(function (id) {
        var u = byId[id];
        if (u) dst.appendChild(new Option(u.label, String(u.id)));
      });
    }

    var leaderIds = init.leaderIds && init.leaderIds.length ? init.leaderIds : init.managerId ? [init.managerId] : [];
    clearSelect(mgrDst);
    leaderIds.forEach(function (lid) {
      if (byId[lid]) mgrDst.appendChild(new Option(byId[lid].label, String(lid)));
      else mgrDst.appendChild(new Option("Kullanıcı #" + lid, String(lid)));
    });

    initDestFromIds(memDst, init.memberIds || []);
    initDestFromIds(obsDst, init.observerIds || []);

    Array.prototype.forEach.call(memDst.options, function (mo) {
      removeObserverIfMember(obsDst, parseInt(mo.value, 10));
    });

    refreshAllSources();

    function onMemChange() {
      memberIds(memDst).forEach(function (uid) {
        removeObserverIfMember(obsDst, uid);
      });
      rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
    }

    document.getElementById("micro-proj-mgr-add").addEventListener("click", function () {
      addFromTo(mgrSrc, mgrDst);
      rebuildManagerSource(allUsers, mgrSrc, mgrDst);
    });
    document.getElementById("micro-proj-mgr-rem").addEventListener("click", function () {
      removeFromTo(mgrDst, mgrSrc, function () {
        rebuildManagerSource(allUsers, mgrSrc, mgrDst);
      });
    });

    document.getElementById("micro-proj-mem-add").addEventListener("click", function () {
      addFromTo(memSrc, memDst);
      onMemChange();
      rebuildMemberSource(allUsers, memSrc, memDst);
    });
    document.getElementById("micro-proj-mem-rem").addEventListener("click", function () {
      removeFromTo(memDst, memSrc, function () {
        onMemChange();
        rebuildMemberSource(allUsers, memSrc, memDst);
        rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
      });
    });

    document.getElementById("micro-proj-obs-add").addEventListener("click", function () {
      var sel = selectedOptions(obsSrc);
      for (var i = 0; i < sel.length; i++) {
        var uid = parseInt(sel[i].value, 10);
        if (memberIds(memDst).indexOf(uid) !== -1) {
          toast("warning", "Üye olan kullanıcı gözlemci olamaz; önce üyelikten çıkarın.");
          return;
        }
      }
      addFromTo(obsSrc, obsDst, {
        onAfter: function () {
          rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
        },
      });
      rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
    });
    document.getElementById("micro-proj-obs-rem").addEventListener("click", function () {
      removeFromTo(obsDst, obsSrc, function () {
        rebuildObserverSource(allUsers, obsSrc, obsDst, memDst);
      });
    });

    mgrSrc.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-mgr-add").click();
    });
    mgrDst.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-mgr-rem").click();
    });
    memSrc.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-mem-add").click();
    });
    memDst.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-mem-rem").click();
    });
    obsSrc.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-obs-add").click();
    });
    obsDst.addEventListener("dblclick", function () {
      document.getElementById("micro-proj-obs-rem").click();
    });

    bindFilter("micro-proj-mgr-filter", "micro-proj-mgr-src");
    bindFilter("micro-proj-mem-filter", "micro-proj-mem-src");
    bindFilter("micro-proj-obs-filter", "micro-proj-obs-src");

    form.addEventListener("submit", function (e) {
      if (!mgrDst.options.length) {
        e.preventDefault();
        toast("warning", "En az bir proje lideri seçmelisiniz.");
        return;
      }
      syncHiddenFromSelect(mgrDst, hidLeaders, "leaders");
      syncHiddenFromSelect(memDst, hidMem, "members");
      syncHiddenFromSelect(obsDst, hidObs, "observers");
    });
  });
})();
