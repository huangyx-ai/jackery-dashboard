from flask import Flask, request, jsonify, render_template_string, send_from_directory
import redis
import json
import os

app = Flask(__name__)

# Redis connection
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(REDIS_URL, decode_responses=True)

REDIS_KEY = "jackery_dashboard_data"
EDIT_PASSWORD = os.environ.get("EDIT_PASSWORD", "jackery2026")

# Default data
DEFAULT_DATA = {
    "hero_badge": "日本地区月度达成",
    "hero_sub": "订单收入合计",
    "hero_num": "1.45",
    "hero_rate": "134%",
    "hero_lbl": "总达成率 · 创2025年8月以来历史新高",
    "k1": "2600万", "k1l": "营运利润",
    "k2": "152%",   "k2l": "利润达成率",
    "k3": "18.7%",  "k3l": "利润率",
    # 营运利润
    "p_pk": "152% 达成",
    "p_num": "2600万",
    "p_t1": "达成率 152%", "p_t2": "利润率 18.7%", "p_t3": "超额完成目标",
    "p_pct": "152%",
    "p_b1": "2600万", "p_b1s": "达成 152%", "p_b2": "18.7%",
    # 第三方
    "tp_pk": "8050万 · 174%",
    "tp_num": "8050万",
    "tp_t1": "达成率 174%", "tp_t2": "同比 +65%", "tp_t3": "利润率 18%",
    "tp_pct": "174%",
    "tp_adv": "4.4%",
    "tp_a1": "同比优化 2.6%", "tp_a2": "vs预算优化 3.4%", "tp_a3": "连续一年历史新低",
    "tp_mix1": "32%", "tp_mix2": "52%", "tp_mix3": "+26%",
    "tp_m1v": "32%", "tp_m2v": "52%",
    "tp_b1": "174%", "tp_b2": "65%",
    # 官网
    "w_pk": "3360万 · 124%",
    "w_num": "3360万",
    "w_t1": "达成率 124%", "w_t2": "★ 2025年8月以来历史新高",
    "w_pct": "124%",
    "w_adv": "12%", "w_advs": "vs预算优化 3.2%",
    "w_rate": "124%",
    "w_pct2": "70%", "w_ogsm": "+10%",
    "w_m1": "60%", "w_m2": "70%",
    # 渠道
    "c_pk": "2777万 · 历史新高",
    "c_num": "2777万",
    "c_t1": "★ 成立以来历史新高", "c_t2": "同比 +38%", "c_t3": "利润率 18%",
    "c_pct": "+38%",
    "c_b1": "18%", "c_b1s": "收入达成 200%", "c_b2": "18%",
    "tv_total": "3783台", "tv_badge": "★ 销量历史新高",
    "tv_1": "3783", "tv_2": "2123", "tv_3": "1600",
    # 韩国台湾
    "kr_num": "202万", "kr_yoy": "同比 +110%", "kr_pct": "+110%",
    "tw_yoy": ">100%", "tw_pm": "利润率 40%", "tw_pct": ">100%",
    # 市占
    "amz_sh": "47%", "amz_yoy": "↑ 同比 +8%", "amz_ld": "领先第二名 29%",
    "rt_sh": "43%",  "rt_yoy": "↑ 同比 +5%",  "rt_ld": "领先第二名 27%",
    "amz_yoy2": "+8%", "amz_ld2": "领先第二 29%",
    "rt_yoy2": "+5%",  "rt_ld2": "领先第二 27%",
    # footer
    "footer_sub": "日本 · 韩国 · 台湾 | 月度达成情况"
}

def get_data():
    raw = r.get(REDIS_KEY)
    if raw:
        data = json.loads(raw)
        # fill missing keys with defaults
        for k, v in DEFAULT_DATA.items():
            data.setdefault(k, v)
        return data
    return DEFAULT_DATA.copy()

def save_data(data):
    r.set(REDIS_KEY, json.dumps(data, ensure_ascii=False))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jackery 日本地区达成情况</title>
<style>
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
.btn-save:hover{background:rgba(62,207,110,0.28);}
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
.pwd-box{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:28px 28px;width:300px;text-align:center;}
.pwd-title{font-size:15px;font-weight:600;margin-bottom:6px;}
.pwd-sub{font-size:12px;color:var(--t3);margin-bottom:18px;}
.pwd-input{width:100%;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 14px;font-size:14px;color:var(--t1);outline:none;margin-bottom:12px;text-align:center;letter-spacing:2px;}
.pwd-input:focus{border-color:var(--gold-b);}
.pwd-err{font-size:11px;color:var(--red);margin-bottom:10px;display:none;}
.pwd-btns{display:flex;gap:8px;}
.pwd-confirm{flex:1;background:var(--gold-dim);border:1px solid var(--gold-b);color:var(--gold);border-radius:8px;padding:10px;font-size:13px;font-weight:600;cursor:pointer;}
.pwd-close{flex:1;background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--t2);border-radius:8px;padding:10px;font-size:13px;cursor:pointer;}
</style>
</head>
<body>
<div class="wrap">

<div class="toolbar">
  <div class="toolbar-title">Jackery 日本地区达成情况</div>
  <div class="toolbar-btns">
    <button class="btn btn-edit" id="btnEdit" onclick="showPwd()">✏ 编辑数据</button>
    <button class="btn btn-cancel" id="btnCancel" onclick="cancelEdit()">✕ 取消</button>
    <button class="btn btn-save" id="btnSave" onclick="saveData()">✓ 保存</button>
  </div>
</div>
<div class="edit-hint" id="editHint">点击任意文字或数字直接修改 · 修改后点「保存」同步给所有人</div>
<div class="save-toast" id="saveToast">✓ 已保存，所有人可见</div>

<!-- PASSWORD MODAL -->
<div class="pwd-modal" id="pwdModal">
  <div class="pwd-box">
    <div class="pwd-title">编辑验证</div>
    <div class="pwd-sub">请输入编辑密码</div>
    <input class="pwd-input" type="password" id="pwdInput" placeholder="••••••••" onkeydown="if(event.key==='Enter')confirmPwd()">
    <div class="pwd-err" id="pwdErr">密码错误，请重试</div>
    <div class="pwd-btns">
      <button class="pwd-confirm" onclick="confirmPwd()">确认</button>
      <button class="pwd-close" onclick="closePwd()">取消</button>
    </div>
  </div>
</div>

<!-- HERO -->
<div class="hero">
  <div class="hero-badge">★ <span class="ef" id="hero_badge">{{ d.hero_badge }}</span></div>
  <div class="hero-sub"><span class="ef" id="hero_sub">{{ d.hero_sub }}</span></div>
  <div class="hero-num"><span class="ef" id="hero_num">{{ d.hero_num }}</span><span class="hero-unit">亿</span></div>
  <div class="hero-rate"><span class="ef" id="hero_rate">{{ d.hero_rate }}</span></div>
  <div class="hero-rate-lbl"><span class="ef" id="hero_lbl">{{ d.hero_lbl }}</span></div>
</div>

<div class="band">
  <div class="kpi"><div class="kpi-v"><span class="ef" id="k1">{{ d.k1 }}</span></div><div class="kpi-l"><span class="ef" id="k1l">{{ d.k1l }}</span></div></div>
  <div class="kpi"><div class="kpi-v g"><span class="ef" id="k2">{{ d.k2 }}</span></div><div class="kpi-l"><span class="ef" id="k2l">{{ d.k2l }}</span></div></div>
  <div class="kpi"><div class="kpi-v t"><span class="ef" id="k3">{{ d.k3 }}</span></div><div class="kpi-l"><span class="ef" id="k3l">{{ d.k3l }}</span></div></div>
</div>

<div class="gap"></div>

<!-- 营运利润 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar g"></div><div class="sec-ttl">营运利润达成</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk g"><span class="ef" id="p_pk">{{ d.p_pk }}</span></div>
      <div class="chev open">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:block;">
    <div class="cl g">
      <div class="cl-lbl">营运利润</div>
      <div class="cl-num g"><span class="ef" id="p_num">{{ d.p_num }}</span></div>
      <div class="tags">
        <span class="tag tag-g"><span class="ef" id="p_t1">{{ d.p_t1 }}</span></span>
        <span class="tag tag-t"><span class="ef" id="p_t2">{{ d.p_t2 }}</span></span>
        <span class="tag tag-w"><span class="ef" id="p_t3">{{ d.p_t3 }}</span></span>
      </div>
    </div>
    <div class="pb">
      <div class="pb-top"><span>达成进度</span><span class="ef" id="p_pct">{{ d.p_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill g" style="width:100%"></div></div>
    </div>
    <div class="dv"></div>
    <div class="two">
      <div class="box"><div class="box-l">营运利润</div><div class="box-v o"><span class="ef" id="p_b1">{{ d.p_b1 }}</span></div><div class="box-s"><span class="ef" id="p_b1s">{{ d.p_b1s }}</span></div></div>
      <div class="box"><div class="box-l">利润率</div><div class="box-v g"><span class="ef" id="p_b2">{{ d.p_b2 }}</span></div><div class="box-s">Profit Margin</div></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- 第三方 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar"></div><div class="sec-ttl">第三方电商战果</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk"><span class="ef" id="tp_pk">{{ d.tp_pk }}</span></div>
      <div class="chev open">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:block;">
    <div class="cl">
      <div class="cl-lbl">第三方订单收入</div>
      <div class="cl-num"><span class="ef" id="tp_num">{{ d.tp_num }}</span></div>
      <div class="tags">
        <span class="tag tag-o"><span class="ef" id="tp_t1">{{ d.tp_t1 }}</span></span>
        <span class="tag tag-g"><span class="ef" id="tp_t2">{{ d.tp_t2 }}</span></span>
        <span class="tag tag-t"><span class="ef" id="tp_t3">{{ d.tp_t3 }}</span></span>
      </div>
    </div>
    <div class="pb">
      <div class="pb-top"><span>达成进度</span><span class="ef" id="tp_pct">{{ d.tp_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill" style="width:100%"></div></div>
    </div>
    <div class="dv"></div>
    <div class="cl r" style="margin-bottom:12px;">
      <div class="cl-lbl">销售广告费率</div>
      <div class="cl-num r"><span class="ef" id="tp_adv">{{ d.tp_adv }}</span></div>
      <div class="tags">
        <span class="tag tag-g"><span class="ef" id="tp_a1">{{ d.tp_a1 }}</span></span>
        <span class="tag tag-g"><span class="ef" id="tp_a2">{{ d.tp_a2 }}</span></span>
        <span class="tag tag-r"><span class="ef" id="tp_a3">{{ d.tp_a3 }}</span></span>
      </div>
    </div>
    <div class="dv"></div>
    <div class="ins"><b>1.5度电+</b> 销售占比同比提升 · <b><span class="ef" id="tp_mix1">{{ d.tp_mix1 }}</span></b> → <b class="g"><span class="ef" id="tp_mix2">{{ d.tp_mix2 }}</span></b>，同比拉升 <b><span class="ef" id="tp_mix3">{{ d.tp_mix3 }}</span></b></div>
    <div class="mx">
      <div class="mx-top"><span>去年同期占比</span><span class="ef" id="tp_m1v">{{ d.tp_m1v }}</span></div>
      <div class="mx-bg"><div class="mx-fill dim" style="width:32%"></div></div>
    </div>
    <div class="mx">
      <div class="mx-top"><span>本月占比</span><span class="ef" id="tp_m2v">{{ d.tp_m2v }}</span></div>
      <div class="mx-bg"><div class="mx-fill" style="width:52%"></div></div>
    </div>
    <div class="dv"></div>
    <div class="ins"><b class="t">E1500V2</b> 成功接替 E1000V2，占据春促销售榜单 <b class="t">BSR</b> 席位</div>
    <div class="dv"></div>
    <div class="two">
      <div class="box"><div class="box-l">达成率</div><div class="box-v o"><span class="ef" id="tp_b1">{{ d.tp_b1 }}</span></div><div class="box-s">vs Budget</div></div>
      <div class="box"><div class="box-l">同比增长</div><div class="box-v g"><span class="ef" id="tp_b2">{{ d.tp_b2 }}</span></div><div class="box-s">YoY Growth</div></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- 官网 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar t"></div><div class="sec-ttl">日本官网战果</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk t"><span class="ef" id="w_pk">{{ d.w_pk }}</span></div>
      <div class="chev open">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:block;">
    <div class="cl t">
      <div class="cl-lbl">官网订单收入</div>
      <div class="cl-num t"><span class="ef" id="w_num">{{ d.w_num }}</span></div>
      <div class="tags">
        <span class="tag tag-t"><span class="ef" id="w_t1">{{ d.w_t1 }}</span></span>
        <span class="tag tag-r"><span class="ef" id="w_t2">{{ d.w_t2 }}</span></span>
      </div>
    </div>
    <div class="pb">
      <div class="pb-top"><span>达成进度</span><span class="ef" id="w_pct">{{ d.w_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill t" style="width:100%"></div></div>
    </div>
    <div class="dv"></div>
    <div class="two" style="margin-bottom:14px;">
      <div class="box"><div class="box-l">广告费率</div><div class="box-v r"><span class="ef" id="w_adv">{{ d.w_adv }}</span></div><div class="box-s"><span class="ef" id="w_advs">{{ d.w_advs }}</span></div></div>
      <div class="box"><div class="box-l">达成率</div><div class="box-v t"><span class="ef" id="w_rate">{{ d.w_rate }}</span></div><div class="box-s">vs Budget</div></div>
    </div>
    <div class="ins">⚡ <b class="t">1.5度电+</b> 销售额占比 <b class="t"><span class="ef" id="w_pct2">{{ d.w_pct2 }}</span></b>，超 OGSM 目标 <b class="g"><span class="ef" id="w_ogsm">{{ d.w_ogsm }}</span></b></div>
    <div class="mx">
      <div class="mx-top"><span>OGSM 目标</span><span class="ef" id="w_m1">{{ d.w_m1 }}</span></div>
      <div class="mx-bg"><div class="mx-fill t-dim" style="width:60%"></div></div>
    </div>
    <div class="mx">
      <div class="mx-top"><span>1.5度电+ 实际占比</span><span class="ef" id="w_m2">{{ d.w_m2 }}</span></div>
      <div class="mx-bg"><div class="mx-fill t" style="width:70%"></div></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- 渠道 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar p"></div><div class="sec-ttl">日本渠道战果</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk p"><span class="ef" id="c_pk">{{ d.c_pk }}</span></div>
      <div class="chev open">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:block;">
    <div class="cl p">
      <div class="cl-lbl">渠道签收收入</div>
      <div class="cl-num p"><span class="ef" id="c_num">{{ d.c_num }}</span></div>
      <div class="tags">
        <span class="tag tag-r"><span class="ef" id="c_t1">{{ d.c_t1 }}</span></span>
        <span class="tag tag-g"><span class="ef" id="c_t2">{{ d.c_t2 }}</span></span>
        <span class="tag tag-t"><span class="ef" id="c_t3">{{ d.c_t3 }}</span></span>
      </div>
    </div>
    <div class="pb">
      <div class="pb-top"><span>同比增速</span><span class="ef" id="c_pct">{{ d.c_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill p" style="width:72%"></div></div>
    </div>
    <div class="dv"></div>
    <div class="two" style="margin-bottom:14px;">
      <div class="box"><div class="box-l">3度电收入占比</div><div class="box-v o"><span class="ef" id="c_b1">{{ d.c_b1 }}</span></div><div class="box-s"><span class="ef" id="c_b1s">{{ d.c_b1s }}</span></div></div>
      <div class="box"><div class="box-l">利润率</div><div class="box-v t"><span class="ef" id="c_b2">{{ d.c_b2 }}</span></div><div class="box-s">Profit Margin</div></div>
    </div>
    <div class="cl" style="margin-bottom:12px;">
      <div class="cl-lbl">📺 第二场电视购物</div>
      <div class="cl-num"><span class="ef" id="tv_total">{{ d.tv_total }}</span></div>
      <div class="tags"><span class="tag tag-r"><span class="ef" id="tv_badge">{{ d.tv_badge }}</span></span></div>
    </div>
    <div class="three">
      <div class="box"><div class="box-l">合计</div><div class="box-v o"><span class="ef" id="tv_1">{{ d.tv_1 }}</span></div><div class="box-s">台</div></div>
      <div class="box"><div class="box-l">1度电</div><div class="box-v t"><span class="ef" id="tv_2">{{ d.tv_2 }}</span></div><div class="box-s">台</div></div>
      <div class="box"><div class="box-l">太阳能板</div><div class="box-v g"><span class="ef" id="tv_3">{{ d.tv_3 }}</span></div><div class="box-s">台</div></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- 韩国台湾 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar g"></div><div class="sec-ttl">韩国 &amp; 台湾战果</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk g">双双翻倍增长</div>
      <div class="chev">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:none;">
    <div class="two" style="margin-bottom:14px;">
      <div class="box"><div class="box-l">韩国签收收入</div><div class="box-v g"><span class="ef" id="kr_num">{{ d.kr_num }}</span></div><div class="box-s" style="color:var(--green)"><span class="ef" id="kr_yoy">{{ d.kr_yoy }}</span></div></div>
      <div class="box"><div class="box-l">台湾同比增长</div><div class="box-v g"><span class="ef" id="tw_yoy">{{ d.tw_yoy }}</span></div><div class="box-s" style="color:var(--gold)"><span class="ef" id="tw_pm">{{ d.tw_pm }}</span></div></div>
    </div>
    <div class="pb">
      <div class="pb-top"><span>韩国 YoY</span><span class="ef" id="kr_pct">{{ d.kr_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill g" style="width:100%"></div></div>
    </div>
    <div class="pb" style="margin-top:10px;">
      <div class="pb-top"><span>台湾 YoY</span><span class="ef" id="tw_pct">{{ d.tw_pct }}</span></div>
      <div class="pb-bg"><div class="pb-fill t" style="width:100%"></div></div>
    </div>
  </div>
</div>

<div class="gap"></div>

<!-- 市占率 -->
<div class="sec">
  <div class="sec-hd" onclick="tog(this)">
    <div class="sec-hd-l"><div class="bar"></div><div class="sec-ttl">平台市占率</div></div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div class="sec-pk">连续2年 #1</div>
      <div class="chev">▼</div>
    </div>
  </div>
  <div class="sec-bd" style="display:none;">
    <div class="ins" style="margin-bottom:14px;">★ <b>连续 2 年</b> 双平台市占率排名 <b class="g">第一</b>，持续领跑竞争对手</div>
    <div class="mkt-pair">
      <div class="mkt">
        <div class="mkt-nm">亚马逊</div>
        <div class="mkt-sh"><span class="ef" id="amz_sh">{{ d.amz_sh }}</span></div>
        <div class="mkt-chg"><span class="ef" id="amz_yoy">{{ d.amz_yoy }}</span></div>
        <div class="mkt-ld"><span class="ef" id="amz_ld">{{ d.amz_ld }}</span></div>
        <div class="mkt-bar-bg"><div class="mkt-bar-fill" style="width:47%;height:4px;border-radius:2px;background:linear-gradient(90deg,var(--gold),#ffcc66);"></div></div>
      </div>
      <div class="mkt">
        <div class="mkt-nm">乐天</div>
        <div class="mkt-sh t"><span class="ef" id="rt_sh">{{ d.rt_sh }}</span></div>
        <div class="mkt-chg"><span class="ef" id="rt_yoy">{{ d.rt_yoy }}</span></div>
        <div class="mkt-ld"><span class="ef" id="rt_ld">{{ d.rt_ld }}</span></div>
        <div class="mkt-bar-bg"><div class="mkt-bar-fill" style="width:43%;height:4px;border-radius:2px;background:linear-gradient(90deg,var(--teal),#7dd3fc);"></div></div>
      </div>
    </div>
    <div class="dv"></div>
    <div class="two">
      <div class="box"><div class="box-l">亚马逊 YoY</div><div class="box-v o"><span class="ef" id="amz_yoy2">{{ d.amz_yoy2 }}</span></div><div class="box-s"><span class="ef" id="amz_ld2">{{ d.amz_ld2 }}</span></div></div>
      <div class="box"><div class="box-l">乐天 YoY</div><div class="box-v t"><span class="ef" id="rt_yoy2">{{ d.rt_yoy2 }}</span></div><div class="box-s"><span class="ef" id="rt_ld2">{{ d.rt_ld2 }}</span></div></div>
    </div>
  </div>
</div>

<div class="footer">
  <div class="footer-logo">Jackery</div>
  <div class="footer-sub"><span class="ef" id="footer_sub">{{ d.footer_sub }}</span></div>
</div>

</div>

<script>
var EDIT_PASSWORD = "";
var editing = false;

function tog(hd){
  var bd=hd.nextElementSibling;
  var ch=hd.querySelector('.chev');
  var open=bd.style.display!=='none';
  bd.style.display=open?'none':'block';
  ch.classList.toggle('open',!open);
}

function showPwd(){
  document.getElementById('pwdModal').classList.add('show');
  document.getElementById('pwdInput').value='';
  document.getElementById('pwdErr').style.display='none';
  setTimeout(function(){document.getElementById('pwdInput').focus();},100);
}
function closePwd(){
  document.getElementById('pwdModal').classList.remove('show');
}
function confirmPwd(){
  var pwd=document.getElementById('pwdInput').value;
  fetch('/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pwd})})
  .then(function(r){return r.json();})
  .then(function(res){
    if(res.ok){
      EDIT_PASSWORD=pwd;
      closePwd();
      enterEdit();
    } else {
      document.getElementById('pwdErr').style.display='block';
      document.getElementById('pwdInput').value='';
      document.getElementById('pwdInput').focus();
    }
  });
}

function enterEdit(){
  editing=true;
  document.body.classList.add('editing');
  document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','true');});
  document.getElementById('btnEdit').style.display='none';
  document.getElementById('btnSave').style.display='flex';
  document.getElementById('btnCancel').style.display='flex';
  document.getElementById('editHint').style.display='block';
}

function cancelEdit(){
  editing=false;
  document.body.classList.remove('editing');
  document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','false');el.blur();});
  document.getElementById('btnEdit').style.display='flex';
  document.getElementById('btnSave').style.display='none';
  document.getElementById('btnCancel').style.display='none';
  document.getElementById('editHint').style.display='none';
  location.reload();
}

function saveData(){
  var data={};
  document.querySelectorAll('.ef[id]').forEach(function(el){
    data[el.id]=el.innerText.trim();
  });
  fetch('/save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({data:data,password:EDIT_PASSWORD})
  })
  .then(function(r){return r.json();})
  .then(function(res){
    if(res.ok){
      editing=false;
      document.body.classList.remove('editing');
      document.querySelectorAll('.ef').forEach(function(el){el.setAttribute('contenteditable','false');el.blur();});
      document.getElementById('btnEdit').style.display='flex';
      document.getElementById('btnSave').style.display='none';
      document.getElementById('btnCancel').style.display='none';
      document.getElementById('editHint').style.display='none';
      var t=document.getElementById('saveToast');
      t.style.display='block';
      setTimeout(function(){t.style.display='none';},3000);
    }
  });
}

document.addEventListener('keydown',function(e){
  if(!editing) return;
  if(e.key==='Escape') cancelEdit();
});
</script>
</body>
</html>"""

@app.route("/")
def index():
    d = get_data()
    return render_template_string(HTML_TEMPLATE, d=d)

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
