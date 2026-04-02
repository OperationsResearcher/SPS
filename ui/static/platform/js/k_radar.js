(function () {
  let historyPage = 1;
  let historyLastPage = 1;
  let kpOlgunlukRowsCache = [];
  let crossPaydasRowsCache = [];

  function notify(type, message) {
    if (typeof window.showAppToast === "function") {
      window.showAppToast(type, message);
    } else {
      console.log("[k_radar][" + type + "] " + message);
    }
  }

  async function getJson(url) {
    const resp = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    return resp.json();
  }
  async function postJson(url, body) {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(body || {}),
    });
    const payload = await resp.json();
    if (!resp.ok || payload.success === false) {
      throw new Error((payload && payload.message) || ("HTTP " + resp.status));
    }
    return payload;
  }
  async function putJson(url, body) {
    const resp = await fetch(url, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
      body: JSON.stringify(body || {}),
    });
    const payload = await resp.json();
    if (!resp.ok || payload.success === false) throw new Error((payload && payload.message) || ("HTTP " + resp.status));
    return payload;
  }
  async function deleteJson(url) {
    const resp = await fetch(url, { method: "DELETE", headers: { "X-Requested-With": "XMLHttpRequest" } });
    const payload = await resp.json();
    if (!resp.ok || payload.success === false) throw new Error((payload && payload.message) || ("HTTP " + resp.status));
    return payload;
  }

  function text(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function trendText(tr) {
    if (!tr || typeof tr !== "object") return "-";
    const delta = Number(tr.delta || 0);
    const sign = delta > 0 ? "+" : "";
    const label = tr.label || "stabil";
    const cur = Number(tr.current_period_avg || 0).toFixed(1);
    const prev = Number(tr.previous_period_avg || 0).toFixed(1);
    return label + " (" + sign + delta.toFixed(1) + " puan, son30=" + cur + ", onceki30=" + prev + ")";
  }

  async function loadHub(root) {
    const url = root.dataset.hubUrl;
    const payload = await getJson(url);
    const d = payload.data || {};
    text("kr-total", d.total_score ?? "-");
    text("kr-total-band", (d.total_band || "-").toUpperCase());
    text("kr-ks", d.ks ? d.ks.score : "-");
    text("kr-ks-sub", d.ks ? (d.ks.band || "-").toUpperCase() : "-");
    text("kr-kp", d.kp ? d.kp.score : "-");
    text("kr-kp-sub", d.kp ? (d.kp.band || "-").toUpperCase() : "-");
    text("kr-kpr", d.kpr ? d.kpr.score : "-");
    text("kr-kpr-sub", d.kpr ? (d.kpr.band || "-").toUpperCase() : "-");

    if (root.dataset.recUrl) {
      const recPayload = await getJson(root.dataset.recUrl);
      const items = (recPayload.data && recPayload.data.items) || [];
      const triggers = (recPayload.data && recPayload.data.triggers) || [];
      const container = document.getElementById("kr-recommendations");
      const triggerWrap = document.getElementById("kr-triggers");
      if (container) {
        const canManage = root.dataset.canManage === "1";
        const actionUrl = root.dataset.recActionUrl || "";
        container.innerHTML = items
          .map((item) => {
            const state = item.state || "pending";
            const badge = state && state !== "pending"
              ? '<span style="margin-left:8px; font-size:11px; color:#334155;">[' + state + "]</span>"
              : "";
            if (!canManage) return "<div>- " + item.text + badge + "</div>";
            return (
              '<div style="display:flex; gap:8px; align-items:center; margin-bottom:6px;">' +
              '<span style="flex:1;">- ' +
              item.text +
              badge +
              "</span>" +
              '<button class="mc-btn mc-btn-sm kr-action-btn" data-action="approved" data-item="' +
              encodeURIComponent(item.text) +
              '">Onayla</button>' +
              '<button class="mc-btn mc-btn-sm kr-action-btn" data-action="rejected" data-item="' +
              encodeURIComponent(item.text) +
              '">Reddet</button>' +
              "</div>"
            );
          })
          .join("");
        if (canManage && actionUrl) {
          container.querySelectorAll(".kr-action-btn").forEach((btn) => {
            btn.addEventListener("click", async (ev) => {
              ev.preventDefault();
              const action = btn.dataset.action;
              const item = decodeURIComponent(btn.dataset.item || "");
              try {
                await postJson(actionUrl, { action, item });
                notify("success", "Aksiyon güncellendi.");
                await loadHub(root);
              } catch (e) {
                console.error("[k_radar_action]", e);
                notify("error", e.message || "Aksiyon güncellenemedi.");
              }
            });
          });
        }
      }
      if (triggerWrap) {
        triggerWrap.innerHTML = triggers.length
          ? triggers
              .map((t) => "- [" + (t.rule_code || "-") + "] " + (t.module || "-") + " / " + (t.severity || "-"))
              .join("<br>")
          : "Aktif kural tetikleyici yok.";
      }
    }
    await loadHistory(root);
  }

  async function loadHistory(root) {
    const url = root.dataset.recHistoryUrl;
    const container = document.getElementById("kr-history");
    if (!url || !container) return;
    const stateSel = document.getElementById("kr-history-state");
    const userIdInput = document.getElementById("kr-history-user-id");
    const perPageSel = document.getElementById("kr-history-per-page");
    const pageInfo = document.getElementById("kr-history-page-info");
    const params = new URLSearchParams();
    if (stateSel && stateSel.value) params.set("state", stateSel.value);
    if (userIdInput && userIdInput.value) params.set("user_id", userIdInput.value);
    params.set("page", String(historyPage));
    params.set("per_page", (perPageSel && perPageSel.value) || "10");
    const finalUrl = params.toString() ? url + "?" + params.toString() : url;
    const payload = await getJson(finalUrl);
    const data = payload.data || {};
    const items = data.items || [];
    const pag = data.pagination || { page: 1, pages: 1, total: 0 };
    historyLastPage = Math.max(1, Number(pag.pages || 1));
    historyPage = Math.min(Math.max(1, historyPage), historyLastPage);
    if (pageInfo) {
      pageInfo.textContent = "Sayfa " + pag.page + " / " + pag.pages + " (Toplam: " + pag.total + ")";
    }
    if (!items.length) {
      container.textContent = "Gecmis aksiyon kaydi yok.";
      const prevBtn = document.getElementById("kr-history-prev");
      const nextBtn = document.getElementById("kr-history-next");
      if (prevBtn) prevBtn.disabled = historyPage <= 1;
      if (nextBtn) nextBtn.disabled = true;
      return;
    }
    const rows = items
      .map((i) => {
        const when = i.updated_at ? i.updated_at.replace("T", " ").slice(0, 16) : "-";
        const badgeColor = i.state === "approved" ? "#166534" : i.state === "rejected" ? "#991b1b" : "#334155";
        return (
          "<tr>" +
          "<td style=\"padding:6px; border-bottom:1px solid #e5e7eb;\"><span style=\"color:" + badgeColor + "; font-weight:600;\">" + i.state + "</span></td>" +
          "<td style=\"padding:6px; border-bottom:1px solid #e5e7eb;\">" + i.user_id + "</td>" +
          "<td style=\"padding:6px; border-bottom:1px solid #e5e7eb;\">" + when + "</td>" +
          "<td style=\"padding:6px; border-bottom:1px solid #e5e7eb;\">" + i.recommendation_text + "</td>" +
          "</tr>"
        );
      })
      .join("");
    container.innerHTML =
      "<div style=\"overflow:auto;\">" +
      "<table style=\"width:100%; border-collapse:collapse;\">" +
      "<thead><tr>" +
      "<th style=\"text-align:left; padding:6px; border-bottom:1px solid #e5e7eb;\">Durum</th>" +
      "<th style=\"text-align:left; padding:6px; border-bottom:1px solid #e5e7eb;\">Kullanici</th>" +
      "<th style=\"text-align:left; padding:6px; border-bottom:1px solid #e5e7eb;\">Zaman</th>" +
      "<th style=\"text-align:left; padding:6px; border-bottom:1px solid #e5e7eb;\">Oneri</th>" +
      "</tr></thead>" +
      "<tbody>" + rows + "</tbody></table></div>";

    const csvBtn = document.getElementById("kr-history-csv");
    if (csvBtn) {
      const csvParams = new URLSearchParams();
      if (stateSel && stateSel.value) csvParams.set("state", stateSel.value);
      if (userIdInput && userIdInput.value) csvParams.set("user_id", userIdInput.value);
      const csvBase = root.dataset.recHistoryCsvUrl || "#";
      csvBtn.href = csvParams.toString() ? csvBase + "?" + csvParams.toString() : csvBase;
    }
    const prevBtn = document.getElementById("kr-history-prev");
    const nextBtn = document.getElementById("kr-history-next");
    if (prevBtn) prevBtn.disabled = historyPage <= 1;
    if (nextBtn) nextBtn.disabled = historyPage >= historyLastPage;
  }

  async function loadKs(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-score", d.score ?? "-");
    text("ks-band", (d.band || "-").toUpperCase());
    text("ks-strategy-count", d.strategy_count ?? "-");
    text("ks-process-count", d.process_count ?? "-");
  }

  async function loadKp(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-score", d.score ?? "-");
    text("kp-band", (d.band || "-").toUpperCase());
    text("kp-critical", d.critical_count ?? "-");
    text("kp-kpi-count", d.kpi_count ?? "-");
  }

  async function loadKpr(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kpr-score", d.score ?? "-");
    text("kpr-band", (d.band || "-").toUpperCase());
    text("kpr-critical", d.critical_count ?? "-");
    text("kpr-project-count", d.project_count ?? "-");
  }

  async function loadCross(root) {
    const target = document.getElementById("cross-points");
    const grid = document.getElementById("cross-heatmap-grid");
    const payload = await getJson(root.dataset.url);
    const points = (payload.data && payload.data.points) || [];
    if (!target) return;
    if (!points.length) {
      target.textContent = "Veri bulunamadi.";
      return;
    }
    target.innerHTML = points
      .map(
        (p, idx) =>
          '<button class="mc-btn mc-btn-sm cross-point-btn" data-idx="' +
          idx +
          '" style="margin-right:6px; margin-bottom:6px;">' +
          p.name +
          " (" +
          p.rpn +
          ")</button>"
      )
      .join("");

    if (grid) {
      const cellBase = [];
      for (let y = 5; y >= 1; y--) {
        for (let x = 1; x <= 5; x++) {
          const color =
            x * y >= 16 ? "#fecaca" : x * y >= 9 ? "#fef3c7" : "#dcfce7";
          cellBase.push(
            '<div data-cell="' + x + "-" + y + '" style="border:1px solid #e5e7eb; background:' +
              color +
              '; min-height:28px; border-radius:6px; padding:4px;"></div>'
          );
        }
      }
      grid.innerHTML = cellBase.join("");
      points.forEach((p) => {
        const cell = grid.querySelector('[data-cell="' + p.probability + "-" + p.impact + '"]');
        if (cell) {
          cell.innerHTML +=
            '<div class="cross-point-chip" data-name="' +
            p.name +
            '" style="font-size:11px; background:#0f172a; color:#fff; border-radius:10px; padding:1px 6px; display:inline-block; margin:2px; cursor:pointer;">' +
            p.name +
            "</div>";
        }
      });
    }

    const detailWrap = document.getElementById("cross-heatmap-detail");
    const detailBody = document.getElementById("cross-heatmap-detail-body");
    const renderDetail = (p) => {
      if (!detailWrap || !detailBody || !p) return;
      detailWrap.style.display = "block";
      detailBody.innerHTML =
        "<strong>" + p.name + "</strong><br>" +
        "Kategori: " + (p.category || "-") + "<br>" +
        "Kaynak: " + (p.source || "-") + "<br>" +
        "Olasilik x Etki: " + p.probability + " x " + p.impact + " = " + p.rpn + "<br>" +
        "Oneri: " + (p.recommendation || "Yok");
    };
    target.querySelectorAll(".cross-point-btn").forEach((btn) => {
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        const idx = Number(btn.dataset.idx || -1);
        if (idx >= 0 && points[idx]) renderDetail(points[idx]);
      });
    });
    grid.querySelectorAll(".cross-point-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const name = chip.dataset.name || "";
        const p = points.find((x) => x.name === name);
        if (p) renderDetail(p);
      });
    });
  }

  async function loadKsSwot(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-swot-process-count", d.process_count ?? 0);
    text("ks-swot-low-kpi", d.low_perf_kpi_rows ?? 0);
  }

  async function loadKsPestle(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-pestle-factors", d.factors ?? 0);
    text("ks-pestle-coverage", d.coverage_score ?? 0);
    text("ks-pestle-strategy", d.strategy_count ?? 0);
  }

  async function loadKsTows(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-tows-actions", d.candidate_actions ?? 0);
    text("ks-tows-link-ratio", d.linked_strategy_ratio ?? 0);
  }

  async function loadKsGap(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-gap-kpi", d.kpi_count ?? 0);
    text("ks-gap-rows", d.data_row_count ?? 0);
    text("ks-gap-pressure", d.gap_pressure ?? 0);
  }

  async function loadKsOkr(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-okr-objective", d.objective_count ?? 0);
    text("ks-okr-align", d.alignment_score ?? 0);
  }

  async function loadKsBsc(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-bsc-perspective", d.perspective_coverage ?? 0);
    text("ks-bsc-kpi", d.kpi_count ?? 0);
  }

  async function loadKsEfqm(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-efqm-criteria", d.criterion_coverage ?? 0);
    text("ks-efqm-readiness", d.readiness_score ?? 0);
  }

  async function loadKsHoshin(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-hoshin-focus", d.objective_focus ?? 0);
    text("ks-hoshin-deploy", d.deployment_score ?? 0);
  }

  async function loadKsAnsoff(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-ansoff-options", d.growth_options ?? 0);
    text("ks-ansoff-risk", d.risk_balance ?? 0);
  }

  async function loadKsBcg(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("ks-bcg-portfolio", d.portfolio_count ?? 0);
    text("ks-bcg-balance", d.balance_score ?? 0);
  }

  async function loadKpOlgunluk(root) {
    const payload = await getJson(root.dataset.listUrl);
    kpOlgunlukRowsCache = (payload.data && payload.data.rows) || [];
    renderKpOlgunlukRows(kpOlgunlukRowsCache);
    const applyBtn = document.getElementById("kp-olgunluk-apply");
    if (applyBtn && applyBtn.dataset.bound !== "1") {
      applyBtn.dataset.bound = "1";
      applyBtn.addEventListener("click", (ev) => {
        ev.preventDefault();
        renderKpOlgunlukRows(kpOlgunlukRowsCache);
      });
    }
    const form = document.getElementById("kp-olgunluk-form");
    if (form && root.dataset.canManage === "1" && form.dataset.bound !== "1") {
      form.dataset.bound = "1";
      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(form);
        try {
          await postJson(root.dataset.createUrl, {
            process_id: fd.get("process_id"),
            maturity_level: fd.get("maturity_level"),
            dimension: fd.get("dimension"),
          });
          notify("success", "Olgunluk kaydı eklendi.");
          await loadKpOlgunluk(root);
        } catch (e) {
          console.error("[kp_olgunluk_create]", e);
          notify("error", e.message || "Olgunluk kaydı eklenemedi.");
        }
      });
    }
  }

  async function loadKpDarbogaz(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-darbogaz-critical", d.critical_kpi_count ?? 0);
    text("kp-darbogaz-severity", d.severity_index ?? 0);
    text("kp-darbogaz-trend", trendText(d.trend));
  }

  async function loadKpDegerZinciri(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-dz-mapped", d.mapped_process_count ?? 0);
    text("kp-dz-muda", d.muda_risk ?? 0);
    text("kp-dz-trend", trendText(d.trend));
  }

  async function loadKpPareto(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-pareto-impact", d.top_impact_slice ?? 0);
    text("kp-pareto-kpi", d.kpi_count ?? 0);
    text("kp-pareto-trend", trendText(d.trend));
  }

  async function loadKpSla(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-sla-risk", d.breach_risk ?? 0);
    text("kp-sla-rows", d.observed_rows ?? 0);
    text("kp-sla-trend", trendText(d.trend));
  }

  async function loadKpBenchmark(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-benchmark-score", d.comparability_score ?? 0);
    text("kp-benchmark-rows", d.period_row_count ?? 0);
    text("kp-benchmark-trend", trendText(d.trend));
  }

  async function loadKpOee(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-oee-oee", d.oee_estimate ?? 0);
    text("kp-oee-a", d.availability ?? 0);
    text("kp-oee-p", d.performance ?? 0);
    text("kp-oee-q", d.quality ?? 0);
    text("kp-oee-trend", trendText(d.trend));
  }

  async function loadKpVsm(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-vsm-flow", d.flow_efficiency_estimate ?? 0);
    text("kp-vsm-waste", d.waste_pressure ?? 0);
    text("kp-vsm-trend", trendText(d.trend));
  }

  async function loadKpKapasite(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kp-kapasite-util", d.utilization_estimate ?? 0);
    text("kp-kapasite-pressure", d.resource_pressure ?? 0);
    text("kp-kapasite-trend", trendText(d.trend));
  }

  async function loadKprEvm(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kpr-evm-count", d.snapshot_count ?? 0);
    text("kpr-evm-spi", d.avg_spi ?? 0);
    text("kpr-evm-cpi", d.avg_cpi ?? 0);
  }

  async function loadKprRisk(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kpr-risk-open", d.open_risk_count ?? 0);
    text("kpr-risk-rpn", d.avg_rpn ?? 0);
    text("kpr-risk-high", d.high_risk_count ?? 0);
  }

  async function loadKprKaynakKapasite(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kpr-kapasite-load", d.resource_load ?? 0);
    text("kpr-kapasite-overdue", d.overdue_open_tasks ?? 0);
    text("kpr-kapasite-active", d.active_task_count ?? 0);
  }

  async function loadKprGantt(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("kpr-gantt-tasks", d.timeline_task_count ?? 0);
    text("kpr-gantt-ontime", d.on_time_ratio ?? 0);
  }

  async function loadCrossRekabet(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("cross-rekabet-count", d.record_count ?? 0);
    text("cross-rekabet-gap", d.avg_gap_against_competition ?? 0);
  }

  async function loadCrossA3(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("cross-a3-count", d.report_count ?? 0);
    text("cross-a3-coverage", d.root_cause_coverage ?? 0);
  }

  async function loadCrossAnket(root) {
    const payload = await getJson(root.dataset.url);
    const d = payload.data || {};
    text("cross-anket-count", d.survey_count ?? 0);
    text("cross-anket-score", d.avg_score ?? 0);
  }

  function renderKpOlgunlukRows(rows) {
    const tbody = document.getElementById("kp-olgunluk-rows");
    const filterVal = ((document.getElementById("kp-olgunluk-filter") || {}).value || "").trim();
    const sortVal = ((document.getElementById("kp-olgunluk-sort") || {}).value || "updated_desc").trim();
    let view = Array.isArray(rows) ? rows.slice() : [];
    if (filterVal) {
      view = view.filter((r) => String(r.process_id || "").includes(filterVal));
    }
    if (sortVal === "level_desc") view.sort((a, b) => (b.maturity_level || 0) - (a.maturity_level || 0));
    if (sortVal === "level_asc") view.sort((a, b) => (a.maturity_level || 0) - (b.maturity_level || 0));
    if (sortVal === "updated_asc") view.sort((a, b) => String(a.updated_at || "").localeCompare(String(b.updated_at || "")));
    if (sortVal === "updated_desc") view.sort((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || "")));
    if (tbody) {
      tbody.innerHTML = view.length
        ? view
            .map(
              (r) =>
                "<tr><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                r.process_id +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                r.maturity_level +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                (r.dimension || "-") +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                ((r.updated_at || "").replace("T", " ").slice(0, 16) || "-") +
                "</td>" +
                ((document.getElementById("k-radar-kp-olgunluk-root")?.dataset.canManage === "1")
                  ? ("<td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                    "<button class=\"mc-btn mc-btn-sm kp-edit\" data-id=\"" + r.id + "\" data-level=\"" + r.maturity_level + "\" data-dimension=\"" + encodeURIComponent(r.dimension || "") + "\">Düzenle</button> " +
                    "<button class=\"mc-btn mc-btn-sm kp-del\" data-id=\"" + r.id + "\">Sil</button></td>")
                  : "") +
                "</tr>"
            )
            .join("")
        : "<tr><td colspan=\"5\" style=\"padding:8px; color:#64748b;\">Kayıt bulunamadı.</td></tr>";
      const root = document.getElementById("k-radar-kp-olgunluk-root");
      if (root && root.dataset.canManage === "1") {
        tbody.querySelectorAll(".kp-edit").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const curLevel = btn.dataset.level || "3";
            const curDim = decodeURIComponent(btn.dataset.dimension || "");
            const level = window.prompt("Yeni seviye (1-5):", curLevel);
            if (!level) return;
            const dim = window.prompt("Boyut:", curDim);
            try {
              await putJson(root.dataset.updateBase + id, { maturity_level: Number(level), dimension: dim || "" });
              notify("success", "Kayıt güncellendi.");
              await loadKpOlgunluk(root);
            } catch (e) {
              notify("error", e.message || "Güncelleme başarısız.");
            }
          });
        });
        tbody.querySelectorAll(".kp-del").forEach((btn) => {
          btn.addEventListener("click", async () => {
            if (!window.confirm("Kayıt silinsin mi?")) return;
            const id = btn.dataset.id;
            try {
              await deleteJson(root.dataset.deleteBase + id);
              notify("success", "Kayıt silindi.");
              await loadKpOlgunluk(root);
            } catch (e) {
              notify("error", e.message || "Silme başarısız.");
            }
          });
        });
      }
    }
  }

  async function loadKprCpm(root) {
    const form = document.getElementById("kpr-cpm-form");
    const select = document.getElementById("kpr-cpm-project");
    const doLoad = async () => {
      const pid = select && select.value ? String(select.value) : "";
      if (!pid) return;
      const payload = await getJson(root.dataset.url + "?project_id=" + encodeURIComponent(pid));
      const d = payload.data || {};
      text("kpr-cpm-task-count", d.task_count ?? 0);
      text("kpr-cpm-dep-count", d.dependency_count ?? 0);
      text("kpr-cpm-critical-count", (d.critical_starts || []).length);
      const list = document.getElementById("kpr-cpm-critical-list");
      const empty = document.getElementById("kpr-cpm-empty");
      if (list) {
        const cs = d.critical_starts || [];
        list.innerHTML = cs.length
          ? cs.map((t) => "<div>- [#" + t.id + "] " + t.title + "</div>").join("")
          : "<div style=\"color:#64748b;\">Kritik başlangıç görevi bulunamadı.</div>";
      }
      if (empty) empty.style.display = "none";
      notify("success", "CPM analizi güncellendi.");
    };
    if (form && form.dataset.bound !== "1") {
      form.dataset.bound = "1";
      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        await doLoad();
      });
    }
  }

  async function loadCrossPaydas(root) {
    const payload = await getJson(root.dataset.listUrl);
    crossPaydasRowsCache = (payload.data && payload.data.rows) || [];
    renderCrossPaydasRows(crossPaydasRowsCache);
    const applyBtn = document.getElementById("cross-paydas-apply");
    if (applyBtn && applyBtn.dataset.bound !== "1") {
      applyBtn.dataset.bound = "1";
      applyBtn.addEventListener("click", (ev) => {
        ev.preventDefault();
        renderCrossPaydasRows(crossPaydasRowsCache);
      });
    }
    const form = document.getElementById("cross-paydas-form");
    if (form && root.dataset.canManage === "1" && form.dataset.bound !== "1") {
      form.dataset.bound = "1";
      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const fd = new FormData(form);
        try {
          await postJson(root.dataset.createUrl, {
            name: fd.get("name"),
            role: fd.get("role"),
            influence: fd.get("influence"),
            interest: fd.get("interest"),
            strategy: fd.get("strategy"),
          });
          form.reset();
          notify("success", "Paydaş kaydı eklendi.");
          await loadCrossPaydas(root);
        } catch (e) {
          console.error("[cross_paydas_create]", e);
          notify("error", e.message || "Paydaş kaydı eklenemedi.");
        }
      });
    }
  }

  function renderCrossPaydasRows(rows) {
    const tbody = document.getElementById("cross-paydas-rows");
    const filterVal = (((document.getElementById("cross-paydas-filter") || {}).value || "").trim()).toLowerCase();
    const sortVal = ((document.getElementById("cross-paydas-sort") || {}).value || "updated_desc").trim();
    let view = Array.isArray(rows) ? rows.slice() : [];
    if (filterVal) {
      view = view.filter((r) => {
        const t = ((r.name || "") + " " + (r.role || "")).toLowerCase();
        return t.includes(filterVal);
      });
    }
    if (sortVal === "influence_desc") view.sort((a, b) => (b.influence || 0) - (a.influence || 0));
    if (sortVal === "influence_asc") view.sort((a, b) => (a.influence || 0) - (b.influence || 0));
    if (sortVal === "interest_desc") view.sort((a, b) => (b.interest || 0) - (a.interest || 0));
    if (sortVal === "interest_asc") view.sort((a, b) => (a.interest || 0) - (b.interest || 0));
    if (tbody) {
      tbody.innerHTML = view.length
        ? view
            .map(
              (r) =>
                "<tr><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                r.name +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                (r.role || "-") +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                (r.influence ?? "-") +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                (r.interest ?? "-") +
                "</td><td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                (r.strategy || "-") +
                "</td>" +
                ((document.getElementById("k-radar-cross-paydas-root")?.dataset.canManage === "1")
                  ? ("<td style=\"border-bottom:1px solid #f1f5f9; padding:6px;\">" +
                    "<button class=\"mc-btn mc-btn-sm paydas-edit\" data-id=\"" + r.id + "\" data-name=\"" + encodeURIComponent(r.name || "") + "\" data-role=\"" + encodeURIComponent(r.role || "") + "\" data-inf=\"" + (r.influence || 3) + "\" data-int=\"" + (r.interest || 3) + "\" data-strategy=\"" + encodeURIComponent(r.strategy || "") + "\">Düzenle</button> " +
                    "<button class=\"mc-btn mc-btn-sm paydas-del\" data-id=\"" + r.id + "\">Sil</button></td>")
                  : "") +
                "</tr>"
            )
            .join("")
        : "<tr><td colspan=\"6\" style=\"padding:8px; color:#64748b;\">Kayıt bulunamadı.</td></tr>";
      const root = document.getElementById("k-radar-cross-paydas-root");
      if (root && root.dataset.canManage === "1") {
        tbody.querySelectorAll(".paydas-edit").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const name = window.prompt("Ad:", decodeURIComponent(btn.dataset.name || ""));
            if (!name) return;
            const role = window.prompt("Rol:", decodeURIComponent(btn.dataset.role || "")) || "";
            const influence = Number(window.prompt("Etki (1-5):", btn.dataset.inf || "3") || 3);
            const interest = Number(window.prompt("İlgi (1-5):", btn.dataset.int || "3") || 3);
            const strategy = window.prompt("Strateji:", decodeURIComponent(btn.dataset.strategy || "")) || "";
            try {
              await putJson(root.dataset.updateBase + id, { name, role, influence, interest, strategy });
              notify("success", "Paydaş güncellendi.");
              await loadCrossPaydas(root);
            } catch (e) {
              notify("error", e.message || "Güncelleme başarısız.");
            }
          });
        });
        tbody.querySelectorAll(".paydas-del").forEach((btn) => {
          btn.addEventListener("click", async () => {
            if (!window.confirm("Kayıt silinsin mi?")) return;
            const id = btn.dataset.id;
            try {
              await deleteJson(root.dataset.deleteBase + id);
              notify("success", "Paydaş silindi.");
              await loadCrossPaydas(root);
            } catch (e) {
              notify("error", e.message || "Silme başarısız.");
            }
          });
        });
      }
    }
  }

  async function boot() {
    try {
      const hub = document.getElementById("k-radar-root");
      const ks = document.getElementById("k-radar-ks-root");
      const kp = document.getElementById("k-radar-kp-root");
      const kpr = document.getElementById("k-radar-kpr-root");
      const cross = document.getElementById("k-radar-cross-root");
      const ksSwot = document.getElementById("k-radar-ks-swot-root");
      const ksPestle = document.getElementById("k-radar-ks-pestle-root");
      const ksTows = document.getElementById("k-radar-ks-tows-root");
      const ksGap = document.getElementById("k-radar-ks-gap-root");
      const ksOkr = document.getElementById("k-radar-ks-okr-root");
      const ksBsc = document.getElementById("k-radar-ks-bsc-root");
      const ksEfqm = document.getElementById("k-radar-ks-efqm-root");
      const ksHoshin = document.getElementById("k-radar-ks-hoshin-root");
      const ksAnsoff = document.getElementById("k-radar-ks-ansoff-root");
      const ksBcg = document.getElementById("k-radar-ks-bcg-root");
      const kpOlgunluk = document.getElementById("k-radar-kp-olgunluk-root");
      const kpDarbogaz = document.getElementById("k-radar-kp-darbogaz-root");
      const kpDegerZinciri = document.getElementById("k-radar-kp-deger-zinciri-root");
      const kpPareto = document.getElementById("k-radar-kp-pareto-root");
      const kpSla = document.getElementById("k-radar-kp-sla-root");
      const kpBenchmark = document.getElementById("k-radar-kp-benchmark-root");
      const kpOee = document.getElementById("k-radar-kp-oee-root");
      const kpVsm = document.getElementById("k-radar-kp-vsm-root");
      const kpKapasite = document.getElementById("k-radar-kp-kapasite-root");
      const kprCpm = document.getElementById("k-radar-kpr-cpm-root");
      const kprEvm = document.getElementById("k-radar-kpr-evm-root");
      const kprRisk = document.getElementById("k-radar-kpr-risk-root");
      const kprKaynakKapasite = document.getElementById("k-radar-kpr-kaynak-kapasite-root");
      const kprGantt = document.getElementById("k-radar-kpr-gantt-root");
      const crossPaydas = document.getElementById("k-radar-cross-paydas-root");
      const crossRekabet = document.getElementById("k-radar-cross-rekabet-root");
      const crossA3 = document.getElementById("k-radar-cross-a3-root");
      const crossAnket = document.getElementById("k-radar-cross-anket-root");
      if (hub) await loadHub(hub);
      const historyApply = document.getElementById("kr-history-apply");
      const historyPrev = document.getElementById("kr-history-prev");
      const historyNext = document.getElementById("kr-history-next");
      if (hub && historyApply) {
        historyApply.addEventListener("click", async (ev) => {
          ev.preventDefault();
          historyPage = 1;
          await loadHistory(hub);
        });
      }
      if (hub && historyPrev) {
        historyPrev.addEventListener("click", async (ev) => {
          ev.preventDefault();
          historyPage = Math.max(1, historyPage - 1);
          await loadHistory(hub);
        });
      }
      if (hub && historyNext) {
        historyNext.addEventListener("click", async (ev) => {
          ev.preventDefault();
          if (historyPage < historyLastPage) historyPage += 1;
          await loadHistory(hub);
        });
      }
      if (ks) await loadKs(ks);
      if (kp) await loadKp(kp);
      if (kpr) await loadKpr(kpr);
      if (cross) await loadCross(cross);
      if (ksSwot) await loadKsSwot(ksSwot);
      if (ksPestle) await loadKsPestle(ksPestle);
      if (ksTows) await loadKsTows(ksTows);
      if (ksGap) await loadKsGap(ksGap);
      if (ksOkr) await loadKsOkr(ksOkr);
      if (ksBsc) await loadKsBsc(ksBsc);
      if (ksEfqm) await loadKsEfqm(ksEfqm);
      if (ksHoshin) await loadKsHoshin(ksHoshin);
      if (ksAnsoff) await loadKsAnsoff(ksAnsoff);
      if (ksBcg) await loadKsBcg(ksBcg);
      if (kpOlgunluk) await loadKpOlgunluk(kpOlgunluk);
      if (kpDarbogaz) await loadKpDarbogaz(kpDarbogaz);
      if (kpDegerZinciri) await loadKpDegerZinciri(kpDegerZinciri);
      if (kpPareto) await loadKpPareto(kpPareto);
      if (kpSla) await loadKpSla(kpSla);
      if (kpBenchmark) await loadKpBenchmark(kpBenchmark);
      if (kpOee) await loadKpOee(kpOee);
      if (kpVsm) await loadKpVsm(kpVsm);
      if (kpKapasite) await loadKpKapasite(kpKapasite);
      if (kprCpm) await loadKprCpm(kprCpm);
      if (kprEvm) await loadKprEvm(kprEvm);
      if (kprRisk) await loadKprRisk(kprRisk);
      if (kprKaynakKapasite) await loadKprKaynakKapasite(kprKaynakKapasite);
      if (kprGantt) await loadKprGantt(kprGantt);
      if (crossPaydas) await loadCrossPaydas(crossPaydas);
      if (crossRekabet) await loadCrossRekabet(crossRekabet);
      if (crossA3) await loadCrossA3(crossA3);
      if (crossAnket) await loadCrossAnket(crossAnket);
    } catch (err) {
      console.error("[k_radar]", err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
