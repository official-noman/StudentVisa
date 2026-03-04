"use strict";
(window[
  "webpackJsonp_impage_materials_name_gems_midasbuy_activity_materials@1765266249"
] =
  window[
    "webpackJsonp_impage_materials_name_gems_midasbuy_activity_materials@1765266249"
  ] || []).push([
  ["47902"],
  {
    44903: function (e, t, r) {
      let n;
      (r.r(t),
        r.d(t, {
          default: function () {
            return N;
          },
          BaseMidasbuyEmbed: function () {
            return j;
          },
        }));
      var i = r("40910"),
        o = r("78234"),
        l = r("616"),
        u = r.n(l),
        s = r("48251"),
        a = r("74740"),
        c = r("26964"),
        d = r("63821"),
        b = r("65317"),
        p = r("73534"),
        v = r("92889");
      function f(e, t, r) {
        return (
          t in e
            ? Object.defineProperty(e, t, {
                value: r,
                enumerable: !0,
                configurable: !0,
                writable: !0,
              })
            : (e[t] = r),
          e
        );
      }
      let m = [],
        g = new v.TinyEmitter(),
        h = () => {
          if (m.length && n) {
            let [e, ...t] = m.shift();
            n.notify(e, ...t);
          }
          setTimeout(h, 50);
        },
        y = async () => {
          let e = ["true", "1"].includes((0, b.jS)("debug")),
            t = (0, p.y1)({
              parentOrigin: "*",
              methods: {
                notify: (t, ...r) => {
                  (e &&
                    window.console.log(
                      `[MpgoActivity] ActivityPage received event: ${t}`,
                      ...r,
                    ),
                    g.emit(t, ...r));
                },
              },
            });
          return ((n = await t.promise), h(), n);
        };
      class w extends v.TinyEmitter {
        on(e, t) {
          return (
            g.on(e, t),
            !this.reportListeners.has(e) &&
              (g.on(e, (...t) => {
                this.reportFn(
                  `message_received_${e}`,
                  t.length ? { args: t } : void 0,
                );
              }),
              this.reportListeners.add(e)),
            this
          );
        }
        once(e, t) {
          return (g.once(e, t), this);
        }
        off(e, t) {
          return (g.off(e, t), this);
        }
        emit(e, ...t) {
          return window.parent === window
            ? this
            : (m.push([e, ...t]),
              this.reportFn(
                `message_emit_${e}`,
                t.length ? { args: t } : void 0,
              ),
              this);
        }
        constructor(e) {
          (super(),
            f(this, "reportFn", void 0),
            f(this, "reportListeners", void 0),
            (this.reportFn = e),
            (this.reportListeners = new Set()),
            g.off("report"),
            g.on("report", (e, t) => {
              this.reportFn(`${e}_from_api`, t);
            }));
        }
      }
      var _ = r("49567"),
        O = r("75889"),
        k = r("23430");
      let E = (0, k.u)([
        (e) => {
          let { defaultShowMarketingBar: t, notification: r } = e;
          return {
            defaultShowMarketingBar: t,
            notification: r,
            picNotification: r ? { background: r.background } : void 0,
            showAsPurePicture: !1,
            [k.c]: 2,
          };
        },
      ]);
      function P(e) {
        for (var t = 1; t < arguments.length; t++) {
          var r = null != arguments[t] ? arguments[t] : {},
            n = Object.keys(r);
          ("function" == typeof Object.getOwnPropertySymbols &&
            (n = n.concat(
              Object.getOwnPropertySymbols(r).filter(function (e) {
                return Object.getOwnPropertyDescriptor(r, e).enumerable;
              }),
            )),
            n.forEach(function (t) {
              var n, i, o;
              ((n = e),
                (i = t),
                (o = r[t]),
                i in n
                  ? Object.defineProperty(n, i, {
                      value: o,
                      enumerable: !0,
                      configurable: !0,
                      writable: !0,
                    })
                  : (n[i] = o));
            }));
        }
        return e;
      }
      let j = (e) => {
        var t;
        let {
            defaultShowMarketingBar: r,
            showAsPurePicture: n,
            notification: b,
            picNotification: p,
          } = E(e.data),
          { metadata: v, store: f, domAction: m } = (0, s.Hl)(e),
          { setVerifiedUser: g } = (0, O.ZP)(f),
          { setUserBalance: h } = (0, c.ZP)(f),
          { messenger: k, setMessenger: j } = (0, _.ZP)(f),
          N =
            (null == v
              ? void 0
              : null === (t = v.userData) || void 0 === t
                ? void 0
                : t.token) || "";
        return (
          (0, o.Z)(() => {
            let e = "scrollbar-css";
            if (document.getElementById(e)) return;
            let t = document.createElement("style");
            ((t.id = e),
              (t.innerHTML = `
                    html::-webkit-scrollbar-track, body::-webkit-scrollbar-track {
                    background-color: #000;
                    }
                    ::-webkit-scrollbar {
                    width: 5px;
                    height: 5px;
                    }
                    ::-webkit-scrollbar-track-piece {
                    border-radius: 2px;
                    }
                    ::-webkit-scrollbar-thumb {
                    background-color: rgba(255, 255, 255, 0.8);
                    background-clip: padding-box;
                    min-height: 28px;
                    border-radius: 10px;
                    }
                    ::-webkit-scrollbar-thumb:hover {
                    background-color: rgba(255, 255, 255, 0.6);
                    }
                    `),
              document.head.appendChild(t));
          }),
          (0, l.useEffect)(
            () =>
              f.on(a.wE.statusChange, () => {
                k && k.emit("refreshBalance");
              }),
            [k, f],
          ),
          (0, o.Z)(() => {
            if (window.parent !== window) {
              var t, o, l, u;
              let s = new w((t, r) =>
                m.emit(
                  "VoidClick",
                  P({ module_id: e.instance.id, components_id: t }, r),
                ),
              );
              if (
                (j(s),
                y(),
                !(function () {
                  if (/iPhone/.test(navigator.userAgent)) {
                    let e = document.querySelector("#app");
                    e &&
                      ((e.style.position = "absolute"),
                      (e.style.height = "100%"),
                      (e.style.overflowY = "scroll"));
                  }
                })(),
                (document.body.style.background = (0, d.Ro)()
                  ? "rgba(0,0,0,0)"
                  : "rgb(21, 27, 59)"),
                s.on("setUserInfo", (e) => {
                  g((t) => {
                    var r, n, o;
                    let l =
                        null == t
                          ? void 0
                          : null === (r = t.user) || void 0 === r
                            ? void 0
                            : r.currentBindUser,
                      u = null == e ? void 0 : e.currentBindUser,
                      s =
                        (null == u ? void 0 : u.openid) ===
                          (null == l ? void 0 : l.openid) &&
                        (null == u ? void 0 : u.zoneid) ===
                          (null == l ? void 0 : l.zoneid) &&
                        (null == u ? void 0 : u.userid) ===
                          (null == l ? void 0 : l.userid) &&
                        (null == u ? void 0 : u.verifytype) ===
                          (null == l ? void 0 : l.verifytype);
                    return (
                      !s && f.emit(a.wE.userChange),
                      h((e) => {
                        let t = (s && e ? e.balance : null) || u.balance;
                        return {
                          state: t ? c.qp.FULFILLED : c.qp.NOT_BIND,
                          balance: t,
                        };
                      }),
                      {
                        user:
                          ((n = P(
                            {},
                            (0, i.Z)((null == t ? void 0 : t.user) || {}, e),
                          )),
                          (o = ((o = { token: N }), o)),
                          Object.getOwnPropertyDescriptors
                            ? Object.defineProperties(
                                n,
                                Object.getOwnPropertyDescriptors(o),
                              )
                            : (function (e, t) {
                                var r = Object.keys(e);
                                if (Object.getOwnPropertySymbols) {
                                  var n = Object.getOwnPropertySymbols(e);
                                  r.push.apply(r, n);
                                }
                                return r;
                              })(Object(o)).forEach(function (e) {
                                Object.defineProperty(
                                  n,
                                  e,
                                  Object.getOwnPropertyDescriptor(o, e),
                                );
                              }),
                          n),
                        state: (0, O.V_)(e),
                      }
                    );
                  });
                }),
                s.emit("init"),
                r && !n && b)
              ) {
                let {
                  title: e,
                  contentHtml: r,
                  buttonText: n,
                  imageAside: i,
                  background: l,
                } = b;
                s.emit("setNotificationBar", {
                  title: e,
                  contentHtml: r,
                  status: "canNotCollect",
                  background:
                    null == l
                      ? void 0
                      : null === (t = l[0]) || void 0 === t
                        ? void 0
                        : t.url,
                  buttonText: n,
                  imageAside:
                    null == i
                      ? void 0
                      : null === (o = i[0]) || void 0 === o
                        ? void 0
                        : o.url,
                  buttonAction: "show",
                });
              }
              r &&
                n &&
                p &&
                s.emit("setNotificationBar", {
                  status: "canNotCollect",
                  background:
                    null == p
                      ? void 0
                      : null === (u = p.background) || void 0 === u
                        ? void 0
                        : null === (l = u[0]) || void 0 === l
                          ? void 0
                          : l.url,
                  isPurePicture: !0,
                  buttonAction: "show",
                });
            }
          }),
          u().createElement("div", null)
        );
      };
      var N = j;
    },
    23430: function (e, t, r) {
      r.d(t, {
        c: function () {
          return i;
        },
        u: function () {
          return o;
        },
      });
      var n = r("616");
      let i = "_v";
      function o(e) {
        let t = (t) => {
          let r = t[i] || 1,
            n = e.length + 1;
          return (r === n ? [] : e.slice(r - n)).reduce((e, t, n) => {
            let o = t(e);
            return (
              Object.entries(e).forEach(([e, t]) => {
                e.startsWith("__") && (o[e] = t);
              }),
              (o[i] = r + n + 1),
              o
            );
          }, t);
        };
        return (e) => (0, n.useMemo)(() => t(e), [e]);
      }
    },
    26964: function (e, t, r) {
      r.d(t, {
        ZP: function () {
          return c;
        },
        qp: function () {
          return a;
        },
      });
      var n,
        i = r(16520),
        o = r(33086),
        l = r(99744);
      let u = (0, l.R)(o.e.USER_BALANCE),
        s = (0, l.H)(o.e.USER_BALANCE);
      var a =
        (((n = {}).NOT_QUERIED = "NOT_QUERIED"),
        (n.QUERYING = "QUERYING"),
        (n.NOT_BIND = "NOT_BIND"),
        (n.FULFILLED = "FULFILLED"),
        n);
      function c(e) {
        let t = (0, i.vZ)(e, u, s),
          [r, n] = (0, i.Dr)(t);
        return { userBalance: r, setUserBalance: n };
      }
    },
  },
]);
//# sourceMappingURL=component-base_midasbuy_embed.main.636d57b9ed5140aa.js.map
