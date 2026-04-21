from flask import Flask, request, jsonify, render_template_string
import redis
import json
import os

app = Flask(__name__)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(REDIS_URL, decode_responses=True)
REDIS_KEY = "jackery_dashboard_data"
EDIT_PASSWORD = os.environ.get("EDIT_PASSWORD", "jackery2026")

DEFAULT_DATA = {
    "hero_badge": "日本地区月度达成",
    "hero_sub": "订单收入合计",
    "hero_num": "1.45",
    "hero_rate": "134%",
    "hero_lbl": "总达成率 · 创2025年8月以来历史新高",
    "k1": "2600万", "k1l": "营运利润",
    "k2": "152%", "k2l": "利润达成率",
    "k3": "18.7%", "k3l": "利润率",
    "p_pk": "152% 达成", "p_num": "2600万",
    "p_t1": "达成率 152%", "p_t2": "利润率 18.7%", "p_t3": "超额完成目标",
    "p_pct": "152%", "p_b1": "2600万", "p_b1s": "达成 152%", "p_b2": "18.7%",
    "tp_pk": "8050万 · 174%", "tp_num": "8050万",
    "tp_t1": "达成率 174%", "tp_t2": "同比 +65%", "tp_t3": "利润率 18%",
    "tp_pct": "174%", "tp_adv": "4.4%",
    "tp_a1": "同比优化 2.6%", "tp_a2": "vs预算优化 3.4%", "tp_a3": "连续一年历史新低",
    "tp_mix1": "32%", "tp_mix2": "52%", "tp_mix3": "+26%",
    "tp_m1v": "32%", "tp_m2v": "52%", "tp_b1": "174%", "tp_b2": "65%",
    "w_pk": "3360万 · 124%", "w_num": "3360万",
    "w_t1": "达成率 124%", "w_t2": "★ 2025年8月以来历史新高",
    "w_pct": "124%", "w_adv": "12%", "w_advs": "vs预算优化 3.2%",
    "w_rate": "124%", "w_pct2": "70%", "w_ogsm": "+10%", "w_m1": "60%", "w_m2": "70%",
    "c_pk": "2777万 · 历史新高", "c_num": "2777万",
    "c_t1": "★ 成立以来历史新高", "c_t2": "同比 +38%", "c_t3": "利润率 18%",
    "c_pct": "+38%", "c_b1": "18%", "c_b1s": "收入达成 200%", "c_b2": "18%",
    "tv_total": "3783台", "tv_badge": "★ 销量历史新高",
    "tv_1": "3783", "tv_2": "2123", "tv_3": "1600",
    "kr_num": "202万", "kr_yoy": "同比 +110%", "kr_pct": "+110%",
    "tw_yoy": ">100%", "tw_pm": "利润率 40%", "tw_pct": ">100%",
    "amz_sh": "47%", "amz_yoy": "↑ 同比 +8%", "amz_ld": "领先第二名 29%",
    "rt_sh": "43%", "rt_yoy": "↑ 同比 +5%", "rt_ld": "领先第二名 27%",
    "amz_yoy2": "+8%", "amz_ld2": "领先第二 29%",
    "rt_yoy2": "+5%", "rt_ld2": "领先第二 27%",
    "footer_sub": "日本 · 韩国 · 台湾 | 月度达成情况"
}

def get_data():
    raw = r.get(REDIS_KEY)
    if raw:
        data = json.loads(raw)
        for k, v in DEFAULT_DATA.items():
            data.setdefault(k, v)
        return data
    return DEFAULT_DATA.copy()

def save_data(data):
    r.set(REDIS_KEY, json.dumps(data, ensure_ascii=False))

def build_html(d):
    css = """
    *{margin:0;padding:0;box-sizing:border-box;}
    :root{
      --gold:#F5A623;--gold-dim:rgba(245,166,35,0.15);--gold-b:rgba(245,166,35,0.3);
      --green:#3ecf6e;--green-dim:rgba(62,207,110,0.12);--green-b:rgba(62,207,110,0.3);
      --teal:#38bdf8;--teal-dim:rgba(56,189,248,0.12);--teal-b:rgba(56,189,248,0.3);
      --red:#f87171;--red-dim:rgba(248,113,113,0.12);--red-b:rgba(248,113,113,0.3);
      --purple:#c084fc;--purple-dim:rgba(192,132,252,0.12);--purple-b:rgba(192,132,252,0.3);
      --bg0:#0d0d0d;--bg1:#161616;--bg2:#1e1e1e;--bg3:#252525;
      --border:rgba(255,255,255,0.08);--t1:#fff;--t2:#aaa;--t3:#555;
    }
    body{background:var(--bg0);color:var(--t1);font-family:'PingFang SC','Microsoft YaHei',sans-serif;}
    .wrap{width:420px;margin:0 auto;padding:0 0 60px;}
    .toolbar{position:sticky;top:0;z-index:100;background:rgba(13,13,13,0.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--border);padding:10px 20px;display:flex;align-items:center;justify-content:space-between;}
    .toolbar-title{font-size:13px;color:var(--t2);}
    .toolbar-btns{display:flex;gap:8px;align-items:center;}
    .btn{display:flex;align-items:center;gap:5px;border-radius:20px;padding:7px 16px;font-size:12px;font-weight:600;cursor:pointer;border:none;transition:all 0.2s;}
    .btn-edit{background:var(--gold-dim);border:1px solid var(--gold-b);color:var(--gold);}
    .btn-edit:hover{background:rgba(245,166,35,0.28);}
    .btn-save{background:rgba(62,207,110,0.15);border:1px solid var(--green-b);color:var(--green);display:none;}
    .btn-cancel{background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--t2);display:none;}
    .edit-hint{display:none;background:rgba(245,166,35,0.08);border-bottom:1px solid var(--gold-b);padding:9px 20px;font-size:11px;color:var(--gold);text-align:center;}
    .save-toast{display:none;position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:rgba(62,207,110,0.9);color:#fff;padding:10px 24px;border-radius:20px;font-size:13px;font-weight:600;z-index:999;}
    .ef{display:inline;border-radius:3px;outline:none;transition:background 0.15s;white-space:pre-wrap;word-break:break-all;}
    body.editing .ef{background:rgba(245,166,35,0.1);outline:1px dashed rgba(245,166,35,0.4);cursor:text;min-width:12px;padding:0 2px;}
    body.editing .ef:hover{background:rgba(245,166,35,0.18);}
    body.editing .ef:focus{background:rgba(245,166,35,0.18);outline:2px solid var(--gold);}
    .hero{background:var(--bg1);text-align:center;padding:36px 24px 30px;position:relative;overflow:hidden;}
    .hero::after{content:'';position:absolute;top:-80px;left:50%;transform:translateX(-50%);width:320px;height:220px;background:radial-gradient(ellipse,rgba(245,166,35,0.11) 0%,transparent 70%);pointer-events:none;}
    .hero-badge{display:inline-flex;align-items:center;gap:6px;background:var(--gold-dim);border:1px solid var(--gold-b);border-radius:20px;padding:5px 16px;font-size:11px;color:var(--gold);margin-bottom:16px;}
    .hero-sub{font-size:12px;color:var(--t3);letter-spacing:1px;margin-bottom:5px;}
    .hero-num{font-size:68px;font-weight:800;color:var(--t1);line-height:1;letter-spacing:-2px;}
    .hero-unit{font-size:24px;font-weight:500;color:var(--t2);vertical-align:super;}
    .hero-rate{font-size:48px;font-weight:800;color:var(--gold);margin:10px 0 5px;line-height:1;}
    .hero-rate-lbl{font-size:11px;color:var(--t3);}
    .band{display:flex;background:var(--bg2);border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
    .kpi{flex:1;text-align:center;padding:16px 8px;border-right:1px solid var(--border);}
    .kpi:last-child{border-right:none;}
    .kpi-v{font-size:21px;font-weight:700;color:var(--gold);line-height:1;}
    .kpi-v.g{color:var(--green);}.kpi-v.t{color:var(--teal);}
    .kpi-l{font-size:10px;color:var(--t3);margin-top:5px;}
    .gap{height:8px;background:var(--bg0);}
    .sec{background:var(--bg1);border-top:1px solid var(--border);overflow:hidden;}
    .sec-hd{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;cursor:pointer;user-select:none;transition:background 0.15s;}
    .sec-hd:hover{background:var(--bg2);}
    .sec-hd-l{display:flex;align-items:center;gap:10px;}
    .bar{width:3px;height:20px;border-radius:2px;background:var(--gold);flex-shrink:0;}
    .bar.g{background:var(--green);}.bar.t{background:var(--teal);}.bar.p{background:var(--purple);}.bar.r{background:var(--red);}
    .sec-ttl{font-size:15px;font-weight:600;}
    .sec-pk{font-size:12px;font-weight:700;color:var(--gold);}
    .sec-pk.g{color:var(--green);}.sec-pk.t{color:var(--teal);}.sec-pk.p{color:var(--purple);}
    .chev{font-size:11px;color:var(--t3);transition:transform 0.22s;display:inline-block;}
    .chev.open{transform:rotate(180deg);}
    .sec-bd{padding:0 20px 20px;}
    .cl{border-left:3px solid var(--gold);background:var(--gold-dim);border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:14px;}
    .cl.g{border-left-color:var(--green);background:var(--green-dim);}
    .cl.t{border-left-color:var(--teal);background:var(--teal-dim);}
    .cl.p{border-left-color:var(--purple);background:var(--purple-dim);}
    .cl.r{border-left-color:var(--red);background:var(--red-dim);}
    .cl-lbl{font-size:11px;color:var(--t3);margin-bottom:6px;}
    .cl-num{font-size:44px;font-weight:800;line-height:1;letter-spacing:-1px;color:var(--gold);}
    .cl-num.g{color:var(--green);}.cl-num.t{color:var(--teal);}.cl-num.p{color:var(--purple);}.cl-num.r{color:var(--red);}
    .tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}
    .tag{display:inline-flex;align-items:center;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;}
    .tag-o{background:var(--gold-dim);border:1px solid var(--gold-b);color:var(--gold);}
    .tag-g{background:var(--green-dim);border:1px solid var(--green-b);color:var(--green);}
    .tag-t{background:var(--teal-dim);border:1px solid var(--teal-b);color:var(--teal);}
    .tag-r{background:var(--red-dim);border:1px solid var(--red-b);color:var(--red);}
    .tag-p{background:var(--purple-dim);border:1px solid var(--purple-b);color:var(--purple);}
    .tag-w{background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--t2);}
    .dv{height:1px;background:var(--border);margin:14px 0;}
    .two{display:flex;gap:10px;}.three{display:flex;gap:8px;}
    .box{flex:1;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:14px 12px;text-align:center;}
    .box-l{font-size:11px;color:var(--t3);margin-bottom:6px;}
    .box-v{font-size:25px;font-weight:800;line-height:1;}
    .box-v.o{color:var(--gold);}.box-v.g{color:var(--green);}.box-v.t{color:var(--teal);}.box-v.r{color:var(--red);}
    .box-s{font-size:11px;color:var(--t3);margin-top:5px;}
    .three .box-v{font-size:20px;}
    .pb{margin:10px 0;}.pb-top{display:flex;justify-content:space-between;font-size:11px;color:var(--t3);margin-bottom:4px;}
    .pb-bg{height:6px;background:var(--bg3);border-radius:3px;overflow:hidden;}
    .pb-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--gold),#ffcc66);}
    .pb-fill.g{background:linear-gradient(90deg,var(--green),#86efac);}
    .pb-fill.t{background:linear-gradient(90deg,var(--teal),#7dd3fc);}
    .pb-fill.r{background:linear-gradient(90deg,var(--red),#fca5a5);}
    .pb-fill.p{background:linear-gradient(90deg,var(--purple),#e9d5ff);}
    .ins{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:11px 14px;font-size:12px;color:var(--t2);line-height:1.75;margin-bottom:10px;}
    .ins b{font-weight:700;color:var(--gold);}.ins b.g{color:var(--green);}.ins b.t{color:var(--teal);}
    .mx{margin:8px 0;}.mx-top{display:flex;justify-content:space-between;font-size:11px;color:var(--t3);margin-bottom:4px;}
    .mx-bg{height:10px;background:var(--bg3);border-radius:5px;overflow:hidden;}
    .mx-fill{height:100%;border-radius:5px;background:linear-gradient(90deg,var(--gold),#ffcc66);}
    .mx-fill.dim{background:rgba(245,166,35,0.22);}
    .mx-fill.t{background:linear-gradient(90deg,var(--teal),#7dd3fc);}
    .mx-fill.t-dim{background:rgba(56,189,248,0.18);}
    .mkt-pair{display:flex;gap:10px;}
    .mkt{flex:1;background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px 14px;}
    .mkt-nm{font-size:13px;font-weight:600;color:var(--t2);margin-bottom:8px;}
    .mkt-sh{font-size:40px;font-weight:800;color:var(--gold);line-height:1;}
    .mkt-sh.t{color:var(--teal);}
    .mkt-chg{font-size:12px;color:var(--green);font-weight:600;margin-top:4px;}
    .mkt-ld{font-size:11px;color:var(--t3);margin-top:2px;}
    .mkt-bar-bg{height:4px;background:var(--bg3);border-radius:2px;margin-top:10px;overflow:hidden;}
    .mkt-bar-fill{height:100%;border-radius:2px;}
    .footer{text-align:center;padding:28px 20px 20px;border-top:1px solid var(--border);background:var(--bg1);margin-top:8px;}
    .footer-logo{font-size:22px;font-weight:800;font-style:italic;letter-spacing:4px;color:var(--gold);}
    .footer-sub{font-size:11px;color:var(--t3);margin-top:6px;}
    .pwd-modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:200;align-items:center;justify-content:center;}
    .pwd-modal.show{display:flex;}
    .pwd-box{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:28px;width:300px;text-align:center;}
    .pwd-title{font-size:15px;font-weight:600;margin-bottom:6px;}
    .pwd-sub{font-size:12px;color:var(--t3);margin-bottom:18px;}
    .pwd-input{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 14px;font-size:14px;color:var(--t1);outline:none;margin-bottom:12px;text-align:center;letter-spacing:2px;}
    .pwd-input:focus{border-color:var(--gold-b);}
    .pwd-err{font-size:11px;color:var(--red);margin-bottom:10px;display:none;}
    .pwd-btns{display:flex;gap:8px;}
    .pwd-confirm{flex:1;background:var(--gold-dim);border:1px solid var(--gold-b);color:var(--gold);border-radius:8px;padding:10px;font-size:13px;font-weight:600;cursor:pointer;}
    .pwd-close{flex:1;background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--t2);border-radius:8px;padding:10px;font-size:13px;cursor:pointer;}
    """

    body = """
    <div class="wrap">
      <div class="toolbar">
        <div class="toolbar-title">Jackery 日本地区达成情况</div>
        <div class="toolbar-btns">
          <button class="btn btn-edit" id="btnEdit" onclick="showPwd()">&#9999; 编辑数据</button>
          <button class="btn btn-cancel" id="btnCancel" onclick="cancelEdit()">&#10005; 取消</button>
          <button class="btn btn-save" id="btnSave" onclick="saveData()">&#10003; 保存</button>
        </div>
      </div>
      <div class="edit-hint" id="editHint">点击任意文字或数字直接修改 · 修改后点「保存」同步给所有人</div>
      <div class="save-toast" id="saveToast">&#10003; 已保存，所有人可见</div>
      <div class="pwd-modal" id="pwdModal">
        <div class="pwd-box">
          <div class="pwd-title">编辑验证</div>
          <div class="pwd-sub">请输入编辑密码</div>
          <input class="pwd-input" type="password" id="pwdInput" placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;" onkeydown="if(event.key==='Enter')confirmPwd()">
          <div class="pwd-err" id="pwdErr">密码错误，请重试</div>
          <div class="pwd-btns">
            <button class="pwd-confirm" onclick="confirmPwd()">确认</button>
            <button class="pwd-close" onclick="closePwd()">取消</button>
          </div>
        </div>
      </div>
      <div class="hero">
        <div class="hero-badge">&#9733; {hero_badge}</div>
        <div class="hero-sub">{hero_sub}</div>
        <div class="hero-num">{hero_num}<span class="hero-unit">亿</span></div>
        <div class="hero-rate">{hero_rate}</div>
        <div class="hero-rate-lbl">{hero_lbl}</div>
      </div>
      <div class="band">
        <div class="kpi"><div class="kpi-v">{k1}</div><div class="kpi-l">{k1l}</div></div>
        <div class="kpi"><div class="kpi-v g">{k2}</div><div class="kpi-l">{k2l}</div></div>
        <div class="kpi"><div class="kpi-v t">{k3}</div><div class="kpi-l">{k3l}</div></div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar g"></div><div class="sec-ttl">营运利润达成</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk g">{p_pk}</div><div class="chev open">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:block;">
          <div class="cl g">
            <div class="cl-lbl">营运利润</div>
            <div class="cl-num g">{p_num}</div>
            <div class="tags"><span class="tag tag-g">{p_t1}</span><span class="tag tag-t">{p_t2}</span><span class="tag tag-w">{p_t3}</span></div>
          </div>
          <div class="pb"><div class="pb-top"><span>达成进度</span><span>{p_pct}</span></div><div class="pb-bg"><div class="pb-fill g" style="width:100%"></div></div></div>
          <div class="dv"></div>
          <div class="two">
            <div class="box"><div class="box-l">营运利润</div><div class="box-v o">{p_b1}</div><div class="box-s">{p_b1s}</div></div>
            <div class="box"><div class="box-l">利润率</div><div class="box-v g">{p_b2}</div><div class="box-s">Profit Margin</div></div>
          </div>
        </div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar"></div><div class="sec-ttl">第三方电商战果</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk">{tp_pk}</div><div class="chev open">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:block;">
          <div class="cl">
            <div class="cl-lbl">第三方订单收入</div>
            <div class="cl-num">{tp_num}</div>
            <div class="tags"><span class="tag tag-o">{tp_t1}</span><span class="tag tag-g">{tp_t2}</span><span class="tag tag-t">{tp_t3}</span></div>
          </div>
          <div class="pb"><div class="pb-top"><span>达成进度</span><span>{tp_pct}</span></div><div class="pb-bg"><div class="pb-fill" style="width:100%"></div></div></div>
          <div class="dv"></div>
          <div class="cl r" style="margin-bottom:12px;">
            <div class="cl-lbl">销售广告费率</div>
            <div class="cl-num r">{tp_adv}</div>
            <div class="tags"><span class="tag tag-g">{tp_a1}</span><span class="tag tag-g">{tp_a2}</span><span class="tag tag-r">{tp_a3}</span></div>
          </div>
          <div class="dv"></div>
          <div class="ins"><b>1.5度电+</b> 销售占比同比提升 · <b>{tp_mix1}</b> &#8594; <b class="g">{tp_mix2}</b>，同比拉升 <b>{tp_mix3}</b></div>
          <div class="mx"><div class="mx-top"><span>去年同期占比</span><span>{tp_m1v}</span></div><div class="mx-bg"><div class="mx-fill dim" style="width:32%"></div></div></div>
          <div class="mx"><div class="mx-top"><span>本月占比</span><span>{tp_m2v}</span></div><div class="mx-bg"><div class="mx-fill" style="width:52%"></div></div></div>
          <div class="dv"></div>
          <div class="ins"><b class="t">E1500V2</b> 成功接替 E1000V2，占据春促销售榜单 <b class="t">BSR</b> 席位</div>
          <div class="dv"></div>
          <div class="two">
            <div class="box"><div class="box-l">达成率</div><div class="box-v o">{tp_b1}</div><div class="box-s">vs Budget</div></div>
            <div class="box"><div class="box-l">同比增长</div><div class="box-v g">{tp_b2}</div><div class="box-s">YoY Growth</div></div>
          </div>
        </div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar t"></div><div class="sec-ttl">日本官网战果</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk t">{w_pk}</div><div class="chev open">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:block;">
          <div class="cl t">
            <div class="cl-lbl">官网订单收入</div>
            <div class="cl-num t">{w_num}</div>
            <div class="tags"><span class="tag tag-t">{w_t1}</span><span class="tag tag-r">{w_t2}</span></div>
          </div>
          <div class="pb"><div class="pb-top"><span>达成进度</span><span>{w_pct}</span></div><div class="pb-bg"><div class="pb-fill t" style="width:100%"></div></div></div>
          <div class="dv"></div>
          <div class="two" style="margin-bottom:14px;">
            <div class="box"><div class="box-l">广告费率</div><div class="box-v r">{w_adv}</div><div class="box-s">{w_advs}</div></div>
            <div class="box"><div class="box-l">达成率</div><div class="box-v t">{w_rate}</div><div class="box-s">vs Budget</div></div>
          </div>
          <div class="ins">&#9889; <b class="t">1.5度电+</b> 销售额占比 <b class="t">{w_pct2}</b>，超 OGSM 目标 <b class="g">{w_ogsm}</b></div>
          <div class="mx"><div class="mx-top"><span>OGSM 目标</span><span>{w_m1}</span></div><div class="mx-bg"><div class="mx-fill t-dim" style="width:60%"></div></div></div>
          <div class="mx"><div class="mx-top"><span>1.5度电+ 实际占比</span><span>{w_m2}</span></div><div class="mx-bg"><div class="mx-fill t" style="width:70%"></div></div></div>
        </div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar p"></div><div class="sec-ttl">日本渠道战果</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk p">{c_pk}</div><div class="chev open">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:block;">
          <div class="cl p">
            <div class="cl-lbl">渠道签收收入</div>
            <div class="cl-num p">{c_num}</div>
            <div class="tags"><span class="tag tag-r">{c_t1}</span><span class="tag tag-g">{c_t2}</span><span class="tag tag-t">{c_t3}</span></div>
          </div>
          <div class="pb"><div class="pb-top"><span>同比增速</span><span>{c_pct}</span></div><div class="pb-bg"><div class="pb-fill p" style="width:72%"></div></div></div>
          <div class="dv"></div>
          <div class="two" style="margin-bottom:14px;">
            <div class="box"><div class="box-l">3度电收入占比</div><div class="box-v o">{c_b1}</div><div class="box-s">{c_b1s}</div></div>
            <div class="box"><div class="box-l">利润率</div><div class="box-v t">{c_b2}</div><div class="box-s">Profit Margin</div></div>
          </div>
          <div class="cl" style="margin-bottom:12px;">
            <div class="cl-lbl">&#128250; 第二场电视购物</div>
            <div class="cl-num">{tv_total}</div>
            <div class="tags"><span class="tag tag-r">{tv_badge}</span></div>
          </div>
          <div class="three">
            <div class="box"><div class="box-l">合计</div><div class="box-v o">{tv_1}</div><div class="box-s">台</div></div>
            <div class="box"><div class="box-l">1度电</div><div class="box-v t">{tv_2}</div><div class="box-s">台</div></div>
            <div class="box"><div class="box-l">太阳能板</div><div class="box-v g">{tv_3}</div><div class="box-s">台</div></div>
          </div>
        </div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar g"></div><div class="sec-ttl">韩国 &amp; 台湾战果</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk g">双双翻倍增长</div><div class="chev">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:none;">
          <div class="two" style="margin-bottom:14px;">
            <div class="box"><div class="box-l">韩国签收收入</div><div class="box-v g">{kr_num}</div><div class="box-s" style="color:var(--green)">{kr_yoy}</div></div>
            <div class="box"><div class="box-l">台湾同比增长</div><div class="box-v g">{tw_yoy}</div><div class="box-s" style="color:var(--gold)">{tw_pm}</div></div>
          </div>
          <div class="pb"><div class="pb-top"><span>韩国 YoY</span><span>{kr_pct}</span></div><div class="pb-bg"><div class="pb-fill g" style="width:100%"></div></div></div>
          <div class="pb" style="margin-top:10px;"><div class="pb-top"><span>台湾 YoY</span><span>{tw_pct}</span></div><div class="pb-bg"><div class="pb-fill t" style="width:100%"></div></div></div>
        </div>
      </div>
      <div class="gap"></div>
      <div class="sec">
        <div class="sec-hd" onclick="tog(this)">
          <div class="sec-hd-l"><div class="bar"></div><div class="sec-ttl">平台市占率</div></div>
          <div style="display:flex;align-items:center;gap:10px;"><div class="sec-pk">连续2年 #1</div><div class="chev">&#9660;</div></div>
        </div>
        <div class="sec-bd" style="display:none;">
          <div class="ins" style="margin-bottom:14px;">&#9733; <b>连续 2 年</b> 双平台市占率排名 <b class="g">第一</b>，持续领跑竞争对手</div>
          <div class="mkt-pair">
            <div class="mkt">
              <div class="mkt-nm">亚马逊</div>
              <div class="mkt-sh">{amz_sh}</div>
              <div class="mkt-chg">{amz_yoy}</div>
              <div class="mkt-ld">{amz_ld}</div>
              <div class="mkt-bar-bg"><div class="mkt-bar-fill" style="width:47%;height:4px;border-radius:2px;background:linear-gradient(90deg,#F5A623,#ffcc66);"></div></div>
            </div>
            <div class="mkt">
              <div class="mkt-nm">乐天</div>
              <div class="mkt-sh t">{rt_sh}</div>
              <div class="mkt-chg">{rt_yoy}</div>
              <div class="mkt-ld">{rt_ld}</div>
              <div class="mkt-bar-bg"><div class="mkt-bar-fill" style="width:43%;height:4px;border-radius:2px;background:linear-gradient(90deg,#38bdf8,#7dd3fc);"></div></div>
            </div>
          </div>
          <div class="dv"></div>
          <div class="two">
            <div class="box"><div class="box-l">亚马逊 YoY</div><div class="box-v o">{amz_yoy2}</div><div class="box-s">{amz_ld2}</div></div>
            <div class="box"><div class="box-l">乐天 YoY</div><div class="box-v t">{rt_yoy2}</div><div class="box-s">{rt_ld2}</div></div>
          </div>
        </div>
      </div>
      <div class="footer">
        <div class="footer-logo">Jackery</div>
        <div class="footer-sub">{footer_sub}</div>
      </div>
    </div>
    """.format(**{k: '<span class="ef" id="{0}">{1}</span>'.format(k, v) for k, v in d.items()})

    js = """
    var EDIT_PASSWORD = "";
    var editing = false;
    function tog(hd){var bd=hd.nextElementSibling;var ch=hd.querySelector('.chev');var open=bd.style.display!=='none';bd.style.display=open?'none':'block';ch.classList.toggle('open',!open);}
    function showPwd(){document.getElementById('pwdModal').classList.add('show');document.getElementById('pwdInput').value='';document.getElementById('pwdErr').style.display='none';setTimeout(function(){document.getElementById('pwdInput').focus();},100);}
    function closePwd(){document.getElementById('pwdModal').classList.remove('show');}
    function confirmPwd(){var pwd=document.getElementById('pwdInput').value;fetch('/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pwd})}).then(function(r){return r.json();}).then(function(res){if(res.ok){EDIT_PASSWORD=pwd;closePwd();enterEdit();}else{document.getElementById('pwdErr').style.display='block';document.getElementById('pwdInput').value='';document.getElementById('pwdInput').focus();}});}
    function enterEdit(){editing=true;document.body.classList.add('editing');document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','true');});document.getElementById('btnEdit').style.display='none';document.getElementById('btnSave').style.display='flex';document.getElementById('btnCancel').style.display='flex';document.getElementById('editHint').style.display='block';}
    function cancelEdit(){editing=false;document.body.classList.remove('editing');document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','false');el.blur();});document.getElementById('btnEdit').style.display='flex';document.getElementById('btnSave').style.display='none';document.getElementById('btnCancel').style.display='none';document.getElementById('editHint').style.display='none';location.reload();}
    function saveData(){var data={};document.querySelectorAll('.ef[id]').forEach(function(el){data[el.id]=el.innerText.trim();});fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data:data,password:EDIT_PASSWORD})}).then(function(r){return r.json();}).then(function(res){if(res.ok){editing=false;document.body.classList.remove('editing');document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','false');el.blur();});document.getElementById('btnEdit').style.display='flex';document.getElementById('btnSave').style.display='none';document.getElementById('btnCancel').style.display='none';document.getElementById('editHint').style.display='none';var t=document.getElementById('saveToast');t.style.display='block';setTimeout(function(){t.style.display='none';},3000);}});}
    document.addEventListener('keydown',function(e){if(!editing)return;if(e.key==='Escape')cancelEdit();});
    """

    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jackery 日本地区达成情况</title>
<style>{css}</style>
</head>
<body>
{body}
<script>{js}</script>
</body>
</html>""".format(css=css, body=body, js=js)


# ── 原有路由 ──────────────────────────────────────────────────────
@app.route("/")
def index():
    d = get_data()
    return build_html(d)

@app.route("/verify", methods=["POST"])
def verify():
    payload = request.get_json()
    pwd = payload.get("password", "")
    if pwd == EDIT_PASSWORD:
        return jsonify({"ok": True})
    return jsonify({"ok": False})

@app.route("/save", methods=["POST"])
def save():
    payload = request.get_json()
    if payload.get("password") != EDIT_PASSWORD:
        return jsonify({"ok": False, "error": "Unauthorized"})
    new_data = payload.get("data", {})
    current = get_data()
    current.update(new_data)
    save_data(current)
    return jsonify({"ok": True})


# ── SKU 看板新路由 ────────────────────────────────────────────────
SKU_REDIS_KEY = "sku_dashboard_data"
SKU_API_SECRET = os.environ.get("SKU_API_SECRET", "jackery_nora_2026")

@app.route("/api/sku-data", methods=["POST"])
def receive_sku_data():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "invalid json"}), 400
    if body.get("secret") != SKU_API_SECRET:
        return jsonify({"error": "unauthorized"}), 401
    payload = {
        "data": body.get("data", []),
        "updated_at": body.get("updated_at"),
    }
    r.set(SKU_REDIS_KEY, json.dumps(payload, ensure_ascii=False))
    return jsonify({"ok": True, "rows": len(payload["data"])}), 200

@app.route("/api/sku-data", methods=["GET"])
def get_sku_data():
    raw = r.get(SKU_REDIS_KEY)
    if not raw:
        return jsonify({"data": [], "updated_at": None}), 200
    return jsonify(json.loads(raw)), 200

@app.route("/sku-dashboard")
def sku_dashboard():
    return build_sku_dashboard_html()

def build_sku_dashboard_html():
    return open_string_sku_html()

def open_string_sku_html():
    return """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日本区 SKU 经营看板</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'PingFang SC','Microsoft YaHei',sans-serif;background:#f5f5f5;color:#1a1a1a;font-size:13px;}
  .header{background:#1F3864;color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;}
  .header h1{font-size:15px;font-weight:500;}
  .sync-info{font-size:11px;opacity:0.7;}
  .container{padding:16px 24px;max-width:1400px;margin:0 auto;}
  .fx-bar{background:#fff;border:1px solid #e0e0e0;border-radius:8px;padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;}
  .fx-bar label{font-size:11px;color:#888;}
  .fx-bar input{width:80px;padding:4px 8px;border:1px solid #ddd;border-radius:4px;font-size:13px;}
  .fx-bar button{padding:5px 14px;background:#E86825;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:12px;}
  .tabs{display:flex;gap:4px;margin-bottom:14px;flex-wrap:wrap;}
  .tab{padding:5px 14px;font-size:12px;border:1px solid #ddd;border-radius:6px;cursor:pointer;background:#fff;color:#666;}
  .tab.active{background:#1F3864;color:#fff;border-color:#1F3864;}
  .kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px;}
  .kpi{background:#fff;border-radius:8px;padding:14px 16px;border:1px solid #e8e8e8;}
  .kpi-label{font-size:11px;color:#888;margin-bottom:4px;}
  .kpi-val{font-size:22px;font-weight:600;color:#1F3864;}
  .whatif{background:#fff;border-radius:8px;padding:14px 16px;border:1px solid #e8e8e8;margin-bottom:14px;}
  .whatif-title{font-size:12px;color:#888;margin-bottom:10px;font-weight:500;}
  .wi-inputs{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-end;margin-bottom:10px;}
  .wi-item{display:flex;flex-direction:column;gap:3px;}
  .wi-item label{font-size:11px;color:#888;}
  .wi-item input{width:90px;padding:5px 8px;border:1px solid #ddd;border-radius:4px;font-size:13px;}
  .wi-results{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
  .wi-card{background:#f9f9f9;border-radius:6px;padding:10px 12px;text-align:center;}
  .wi-card-label{font-size:11px;color:#888;margin-bottom:3px;}
  .wi-card-val{font-size:16px;font-weight:600;}
  .charts-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;}
  .chart-card{background:#fff;border-radius:8px;padding:14px 16px;border:1px solid #e8e8e8;}
  .chart-title{font-size:12px;color:#888;margin-bottom:10px;}
  .legend{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:8px;}
  .leg-i{display:flex;align-items:center;gap:4px;font-size:11px;color:#666;}
  .leg-sq{width:8px;height:8px;border-radius:2px;display:inline-block;}
  .table-card{background:#fff;border-radius:8px;padding:14px 16px;border:1px solid #e8e8e8;margin-bottom:14px;overflow-x:auto;}
  .sku-table{width:100%;border-collapse:collapse;font-size:12px;}
  .sku-table th{text-align:left;padding:7px 10px;color:#888;font-weight:400;border-bottom:1px solid #eee;white-space:nowrap;}
  .sku-table td{padding:7px 10px;border-bottom:1px solid #f0f0f0;white-space:nowrap;}
  .sku-table tr:last-child td{border-bottom:none;}
  .empty{text-align:center;padding:60px;color:#aaa;}
  @media(max-width:700px){.kpi-row{grid-template-columns:1fr 1fr;}.charts-row{grid-template-columns:1fr;}}
</style>
</head>
<body>
<div class="header">
  <h1>日本区 SKU 经营看板</h1>
  <span class="sync-info" id="syncInfo">加载中...</span>
</div>
<div class="container">
  <div class="fx-bar">
    <span style="font-size:11px;color:#888;font-weight:500;">汇率覆盖（可选）</span>
    <div style="display:flex;align-items:center;gap:6px;"><label>JPY/CNY</label><input type="number" id="fx_jpycny" placeholder="来自底稿" step="0.1"></div>
    <div style="display:flex;align-items:center;gap:6px;"><label>JPY/USD</label><input type="number" id="fx_jpyusd" placeholder="来自底稿" step="0.5"></div>
    <button onclick="applyFx()">应用覆盖</button>
    <button onclick="resetFx()" style="background:#888;">重置</button>
    <span id="fxNote" style="font-size:11px;color:#E86825;"></span>
  </div>
  <div class="tabs" id="monthTabs"></div>
  <div class="kpi-row">
    <div class="kpi"><div class="kpi-label">总收入（万JPY）</div><div class="kpi-val" id="kpi_rev">—</div></div>
    <div class="kpi"><div class="kpi-label">综合毛利率</div><div class="kpi-val" id="kpi_gm">—</div></div>
    <div class="kpi"><div class="kpi-label">有效 SKU 数</div><div class="kpi-val" id="kpi_sku">—</div></div>
    <div class="kpi"><div class="kpi-label">总销量</div><div class="kpi-val" id="kpi_vol">—</div></div>
  </div>
  <div class="whatif">
    <div class="whatif-title">What-if 测算 · 在当月数据基础上叠加变动</div>
    <div class="wi-inputs">
      <div class="wi-item"><label>销量变动 %</label><input type="number" id="wi_vol" value="0" step="1" oninput="wiCalc()"></div>
      <div class="wi-item"><label>折扣率变动 pp</label><input type="number" id="wi_disc" value="0" step="0.5" oninput="wiCalc()"></div>
      <div class="wi-item"><label>毛利率变动 pp</label><input type="number" id="wi_gm" value="0" step="0.5" oninput="wiCalc()"></div>
      <div class="wi-item"><label>汇率 JPY/CNY</label><input type="number" id="wi_fx" placeholder="当前值" step="0.1" oninput="wiCalc()"></div>
    </div>
    <div class="wi-results">
      <div class="wi-card"><div class="wi-card-label">收入变动（万JPY）</div><div class="wi-card-val" id="wi_r1">—</div></div>
      <div class="wi-card"><div class="wi-card-label">毛利额变动（万JPY）</div><div class="wi-card-val" id="wi_r2">—</div></div>
      <div class="wi-card"><div class="wi-card-label">毛利率变动后</div><div class="wi-card-val" id="wi_r3">—</div></div>
    </div>
  </div>
  <div class="charts-row">
    <div class="chart-card">
      <div class="chart-title">收入 by SKU（万JPY）</div>
      <div class="legend" id="revLegend"></div>
      <div style="position:relative;width:100%;height:200px;"><canvas id="revChart" role="img" aria-label="Revenue by SKU"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">毛利率 by SKU</div>
      <div style="position:relative;width:100%;height:200px;"><canvas id="gmChart" role="img" aria-label="GM rate by SKU"></canvas></div>
    </div>
  </div>
  <div class="chart-card" style="margin-bottom:14px;">
    <div class="chart-title">月度趋势 · 收入（柱）＋ 毛利率（线）</div>
    <div class="legend">
      <span class="leg-i"><span class="leg-sq" style="background:#B5D4F4"></span>收入（万JPY）</span>
      <span class="leg-i"><span class="leg-sq" style="background:#1D9E75"></span>毛利率%</span>
    </div>
    <div style="position:relative;width:100%;height:200px;"><canvas id="trendChart" role="img" aria-label="Monthly trend"></canvas></div>
  </div>
  <div class="table-card">
    <div class="chart-title" style="margin-bottom:10px;">SKU 明细</div>
    <table class="sku-table">
      <thead><tr><th>产品</th><th>系列</th><th>容量段</th><th>渠道</th><th>销量</th><th>收入（万JPY）</th><th>毛利额（万JPY）</th><th>毛利率</th><th>汇率</th></tr></thead>
      <tbody id="skuTbody"><tr><td colspan="9" class="empty">加载中...</td></tr></tbody>
    </table>
  </div>
</div>
<script>
const COLORS=['#378ADD','#1D9E75','#D85A30','#D4537E','#7F77DD','#BA7517','#E24B4A','#5DCAA5','#EF9F27','#85B7EB'];
let allData=[],months=[],activeMonth='';
let revChart,gmChart,trendChart;

async function loadData(){
  try{
    const res=await fetch('/api/sku-data');
    const json=await res.json();
    allData=json.data||[];
    const updAt=json.updated_at?new Date(json.updated_at).toLocaleString('zh-CN'):'未知';
    document.getElementById('syncInfo').textContent='上次同步：'+updAt;
    months=[...new Set(allData.map(r=>r.month))].sort();
    activeMonth=months[months.length-1]||'';
    buildTabs();render();
  }catch(e){
    document.getElementById('syncInfo').textContent='加载失败';
    document.getElementById('skuTbody').innerHTML='<tr><td colspan="9" class="empty">暂无数据，请先从 Google Sheets 推送</td></tr>';
  }
}

function buildTabs(){
  document.getElementById('monthTabs').innerHTML=months.map(m=>
    '<button class="tab '+(m===activeMonth?'active':'')+'" onclick="switchMonth(\''+m+'\')">'+m+'</button>').join('');
}

function switchMonth(m){activeMonth=m;buildTabs();render();}

function applyFx(){document.getElementById('fxNote').textContent='已覆盖汇率（不影响底稿）';render();}
function resetFx(){document.getElementById('fx_jpycny').value='';document.getElementById('fx_jpyusd').value='';document.getElementById('fxNote').textContent='';render();}

function render(){
  if(!activeMonth)return;
  const rows=allData.filter(r=>r.month===activeMonth&&(r.revenue>0||r.volume>0));
  const totalRev=rows.reduce((s,r)=>s+r.revenue,0);
  const totalGm=rows.reduce((s,r)=>s+r.gmAmount,0);
  const totalVol=rows.reduce((s,r)=>s+r.volume,0);
  const gmRate=totalRev>0?totalGm/totalRev:0;
  const activeSku=[...new Set(rows.map(r=>r.sku))].length;
  document.getElementById('kpi_rev').textContent=(totalRev/10000).toFixed(1)+'万';
  const gmEl=document.getElementById('kpi_gm');
  gmEl.textContent=(gmRate*100).toFixed(1)+'%';
  gmEl.style.color=gmRate>=0.4?'#1D9E75':gmRate>=0.3?'#E86825':'#E24B4A';
  document.getElementById('kpi_sku').textContent=activeSku;
  document.getElementById('kpi_vol').textContent=totalVol.toLocaleString();
  const skuMap={};
  rows.forEach(r=>{
    if(!skuMap[r.sku])skuMap[r.sku]={sku:r.sku,series:r.series,capacity:r.capacity,channel:r.channel,vol:0,rev:0,gm:0,fx:r.fx};
    skuMap[r.sku].vol+=r.volume;skuMap[r.sku].rev+=r.revenue;skuMap[r.sku].gm+=r.gmAmount;
  });
  const skus=Object.values(skuMap).sort((a,b)=>b.rev-a.rev);
  document.getElementById('skuTbody').innerHTML=skus.length?skus.map((s,i)=>{
    const gmR=s.rev>0?s.gm/s.rev:0;
    const gmColor=gmR>=0.4?'#1D9E75':gmR>=0.3?'#E86825':'#E24B4A';
    return '<tr><td style="font-weight:500;border-left:3px solid '+COLORS[i%COLORS.length]+';padding-left:8px;">'+s.sku+'</td><td>'+(s.series||'—')+'</td><td>'+(s.capacity||'—')+'</td><td>'+(s.channel||'—')+'</td><td>'+s.vol.toLocaleString()+'</td><td>'+(s.rev/10000).toFixed(1)+'</td><td>'+(s.gm/10000).toFixed(1)+'</td><td style="color:'+gmColor+';font-weight:500;">'+(gmR*100).toFixed(1)+'%</td><td>'+(s.fx||'—')+'</td></tr>';
  }).join(''):'<tr><td colspan="9" class="empty">当月无数据</td></tr>';
  buildRevChart(skus);buildGmChart(skus);buildTrendChart();wiCalc();
}

function buildRevChart(skus){
  if(revChart)revChart.destroy();
  document.getElementById('revLegend').innerHTML=skus.slice(0,6).map((s,i)=>'<span class="leg-i"><span class="leg-sq" style="background:'+COLORS[i]+'"></span>'+s.sku+'</span>').join('');
  revChart=new Chart(document.getElementById('revChart'),{type:'bar',data:{labels:skus.map(s=>s.sku),datasets:[{data:skus.map(s=>+(s.rev/10000).toFixed(1)),backgroundColor:skus.map((_,i)=>COLORS[i%COLORS.length]),borderRadius:4,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{font:{size:10}},grid:{display:false}},y:{ticks:{font:{size:10},callback:v=>v+'万'},grid:{color:'rgba(0,0,0,0.05)'}}}}});
}

function buildGmChart(skus){
  if(gmChart)gmChart.destroy();
  const vals=skus.map(s=>s.rev>0?+((s.gm/s.rev*100).toFixed(1)):0);
  gmChart=new Chart(document.getElementById('gmChart'),{type:'bar',data:{labels:skus.map(s=>s.sku),datasets:[{data:vals,backgroundColor:vals.map(v=>v>=40?'#1D9E75':v>=30?'#E86825':'#E24B4A'),borderRadius:4,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{font:{size:10}},grid:{display:false}},y:{ticks:{font:{size:10},callback:v=>v+'%'},grid:{color:'rgba(0,0,0,0.05)'},min:0,max:70}}}});
}

function buildTrendChart(){
  if(trendChart)trendChart.destroy();
  const tRevs=months.map(m=>{const rs=allData.filter(r=>r.month===m&&r.revenue>0);return+(rs.reduce((s,r)=>s+r.revenue,0)/10000).toFixed(1);});
  const tGms=months.map(m=>{const rs=allData.filter(r=>r.month===m&&r.revenue>0);const rev=rs.reduce((s,r)=>s+r.revenue,0);const gm=rs.reduce((s,r)=>s+r.gmAmount,0);return rev>0?+((gm/rev*100).toFixed(1)):null;});
  trendChart=new Chart(document.getElementById('trendChart'),{type:'bar',data:{labels:months,datasets:[{type:'bar',label:'收入',data:tRevs,backgroundColor:'#B5D4F4',yAxisID:'y',order:2,borderRadius:3},{type:'line',label:'毛利率%',data:tGms,borderColor:'#1D9E75',backgroundColor:'transparent',pointRadius:3,yAxisID:'y2',order:1,tension:0.3}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{font:{size:10}},grid:{display:false}},y:{position:'left',ticks:{font:{size:10},callback:v=>v+'万'},grid:{color:'rgba(0,0,0,0.05)'}},y2:{position:'right',ticks:{font:{size:10},callback:v=>v+'%'},grid:{display:false}}}}});
}

function wiCalc(){
  const rows=allData.filter(r=>r.month===activeMonth&&r.revenue>0);
  if(!rows.length)return;
  const baseRev=rows.reduce((s,r)=>s+r.revenue,0);
  const baseGm=rows.reduce((s,r)=>s+r.gmAmount,0);
  const baseGmRate=baseRev>0?baseGm/baseRev:0;
  const volDelta=(parseFloat(document.getElementById('wi_vol').value)||0)/100;
  const discDelta=(parseFloat(document.getElementById('wi_disc').value)||0)/100;
  const gmDelta=(parseFloat(document.getElementById('wi_gm').value)||0)/100;
  const fxNew=parseFloat(document.getElementById('wi_fx').value)||rows[0]?.fx||0;
  const fxBase=rows[0]?.fx||fxNew;
  const fxImpact=fxBase>0?(fxNew-fxBase)/fxBase:0;
  const newRev=baseRev*(1+volDelta)*(1-discDelta)*(1+fxImpact);
  const newGmRate=Math.min(0.99,Math.max(0,baseGmRate+gmDelta));
  const newGm=newRev*newGmRate;
  const revChange=(newRev-baseRev)/10000;
  const gmChange=(newGm-baseGm)/10000;
  const r1=document.getElementById('wi_r1');
  r1.textContent=(revChange>=0?'+':'')+revChange.toFixed(1)+'万';
  r1.style.color=revChange>=0?'#1D9E75':'#E24B4A';
  const r2=document.getElementById('wi_r2');
  r2.textContent=(gmChange>=0?'+':'')+gmChange.toFixed(1)+'万';
  r2.style.color=gmChange>=0?'#1D9E75':'#E24B4A';
  const r3=document.getElementById('wi_r3');
  r3.textContent=(newGmRate*100).toFixed(1)+'%';
  r3.style.color=newGmRate>=0.4?'#1D9E75':newGmRate>=0.3?'#E86825':'#E24B4A';
}

loadData();
setInterval(loadData,60000);
</script>
</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
