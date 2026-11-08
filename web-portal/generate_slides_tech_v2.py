from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(19, 36, 62)
BLUE = RGBColor(26, 118, 210)
LIGHT = RGBColor(244, 247, 250)
WHITE = RGBColor(255, 255, 255)
TEXT = RGBColor(32, 46, 63)
MUTED = RGBColor(103, 119, 136)
GREEN = RGBColor(18, 150, 111)
RED = RGBColor(208, 71, 71)
BORDER = RGBColor(216, 227, 237)
SOFT = RGBColor(233, 244, 255)


def set_font(run, size=18, bold=False, color=TEXT, name='Kanit'):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.38), Inches(9.8), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.runs[0].font.size = Pt(26)
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = NAVY
    p.runs[0].font.name = 'Kanit'
    if subtitle:
        sub = slide.shapes.add_textbox(Inches(0.72), Inches(0.98), Inches(10.0), Inches(0.35))
        st = sub.text_frame
        st.paragraphs[0].text = subtitle
        st.paragraphs[0].runs[0].font.size = Pt(11)
        st.paragraphs[0].runs[0].font.color.rgb = MUTED
        st.paragraphs[0].runs[0].font.name = 'Kanit'


def add_bullet_list(slide, items, left=0.8, top=1.5, width=11.1, height=5.0):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.bullet = True
        p.space_after = Pt(8)
        p.runs[0].font.name = 'Kanit'
        p.runs[0].font.size = Pt(18)
        p.runs[0].font.color.rgb = TEXT


def draw_box(slide, x, y, w, h, title, body, fill=WHITE, accent=BLUE, title_size=16, body_size=11):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = fill
    box.line.color.rgb = BORDER
    box.line.width = Pt(1.2)
    header = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.12), Inches(w - 0.24), Inches(0.4))
    htf = header.text_frame
    hp = htf.paragraphs[0]
    hp.text = title
    hp.alignment = PP_ALIGN.CENTER
    hp.runs[0].font.name = 'Kanit'
    hp.runs[0].font.size = Pt(title_size)
    hp.runs[0].font.bold = True
    hp.runs[0].font.color.rgb = accent

    body_box = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.56), Inches(w - 0.24), Inches(h - 0.65))
    bt = body_box.text_frame
    bt.word_wrap = True
    bp = bt.paragraphs[0]
    bp.text = body
    bp.alignment = PP_ALIGN.CENTER
    bp.runs[0].font.name = 'Kanit'
    bp.runs[0].font.size = Pt(body_size)
    bp.runs[0].font.color.rgb = TEXT


def draw_arrow(slide, x1, y1, x2, y2, color=BLUE):
    line = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x1), Inches(y1), Inches(x2-x1), Inches(y2-y1))
    line.fill.solid(); line.fill.fore_color.rgb = color
    line.line.fill.background()

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.33), Inches(0.45))
bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
logo = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(0.8), Inches(0.9), Inches(0.9))
logo.fill.solid(); logo.fill.fore_color.rgb = BLUE; logo.line.fill.background(); logo.text = 'A'
logo.text_frame.paragraphs[0].runs[0].font.name = 'Kanit'; logo.text_frame.paragraphs[0].runs[0].font.size = Pt(28); logo.text_frame.paragraphs[0].runs[0].font.bold = True; logo.text_frame.paragraphs[0].runs[0].font.color.rgb = WHITE

box = slide.shapes.add_textbox(Inches(1.95), Inches(0.82), Inches(6.5), Inches(1.1))
tf = box.text_frame
p = tf.paragraphs[0]; p.text = 'AccessFlow RBAC Portal'; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(30); p.runs[0].font.bold=True; p.runs[0].font.color.rgb=NAVY
p2 = tf.add_paragraph(); p2.text = 'ภาพรวมระบบสำหรับทีมพัฒนา'; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(15); p2.runs[0].font.color.rgb = MUTED

info = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.2), Inches(0.9), Inches(3.2), Inches(2.9))
info.fill.solid(); info.fill.fore_color.rgb = WHITE; info.line.color.rgb = BORDER; info.line.width = Pt(1.1)
info.text = 'Nuxt 3\nJWT + RBAC\nBackend Proxy\nFrontend portal'
for idx, para in enumerate(info.text_frame.paragraphs):
    para.runs[0].font.name = 'Kanit'; para.runs[0].font.size = Pt(18 if idx == 0 else 12); para.runs[0].font.bold = idx == 0; para.runs[0].font.color.rgb = NAVY if idx == 0 else MUTED

add_bullet_list(slide, [
    'เว็บแอปสำหรับจัดการสิทธิ์การเข้าถึงและ session ของผู้ใช้งาน',
    'ใช้ JWT เป็นช่องทางยืนยันตัวตน และ RBAC เป็นกลไกควบคุมสิทธิ์',
    'เชื่อมต่อกับ API ฝั่ง .NET ผ่าน proxy local เพื่อหลีกเลี่ยง CORS ในสภาพแวดล้อม dev',
    'มีหน้า login, overview, abatement, permissions, users, sessions'
], left=0.8, top=3.2, width=7.9, height=2.6)

# right stack
for idx, (icon, label) in enumerate([('🔐', 'Security'), ('🧩', 'RBAC'), ('🖥️', 'Portal'), ('📊', 'Audit')]):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(3.3 + idx*0.7), Inches(3.5), Inches(0.55))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE; box.line.color.rgb = BORDER
    tf = box.text_frame; tf.clear(); p = tf.paragraphs[0]; p.text = f'{icon} {label}'; p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(12); p.runs[0].font.color.rgb = NAVY

# Slide 2
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'สถาปัตยกรรมและโครงสร้างระบบ', 'Frontend, proxy, and backend interaction')

# architecture diagram
left_x = 0.7
box_w = 2.4
box_h = 1.45
# client
box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_x), Inches(2.05), Inches(box_w), Inches(box_h))
box.fill.solid(); box.fill.fore_color.rgb = SOFT; box.line.color.rgb = BLUE; box.line.width = Pt(1.3)
text = box.text_frame; p = text.paragraphs[0]; p.text = 'Client\nWeb Portal\nNuxt 3'; p.alignment=PP_ALIGN.CENTER; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(18); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
p2 = text.add_paragraph(); p2.text='Routes, Auth, Session, RBAC'; p2.alignment=PP_ALIGN.CENTER; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(11); p2.runs[0].font.color.rgb = TEXT
# proxy
box2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_x + 3.3), Inches(2.05), Inches(2.4), Inches(box_h))
box2.fill.solid(); box2.fill.fore_color.rgb = SOFT; box2.line.color.rgb = BLUE; box2.line.width = Pt(1.3)
text2 = box2.text_frame; p = text2.paragraphs[0]; p.text='Backend Proxy\nserver/routes/backend'; p.alignment=PP_ALIGN.CENTER; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(17); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
p2 = text2.add_paragraph(); p2.text='maps /backend/* -> API'; p2.alignment=PP_ALIGN.CENTER; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(11); p2.runs[0].font.color.rgb = TEXT
# api
box3 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_x + 6.7), Inches(2.05), Inches(2.5), Inches(box_h))
box3.fill.solid(); box3.fill.fore_color.rgb = SOFT; box3.line.color.rgb = BLUE; box3.line.width = Pt(1.3)
text3 = box3.text_frame; p = text3.paragraphs[0]; p.text='API Service\n.NET Web API'; p.alignment=PP_ALIGN.CENTER; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(17); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
p2 = text3.add_paragraph(); p2.text='JWT validation, RBAC checks'; p2.alignment=PP_ALIGN.CENTER; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(11); p2.runs[0].font.color.rgb = TEXT
# data
box4 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_x + 10.1), Inches(2.05), Inches(2.3), Inches(box_h))
box4.fill.solid(); box4.fill.fore_color.rgb = SOFT; box4.line.color.rgb = BLUE; box4.line.width = Pt(1.3)
text4 = box4.text_frame; p = text4.paragraphs[0]; p.text='Auth Store\nLocalStorage + Session'; p.alignment=PP_ALIGN.CENTER; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(16); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
p2 = text4.add_paragraph(); p2.text='accessToken / refreshToken'; p2.alignment=PP_ALIGN.CENTER; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(11); p2.runs[0].font.color.rgb = TEXT

# arrows
arrow1 = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left_x + 2.4), Inches(2.7), Inches(0.8), Inches(0.2)); arrow1.fill.solid(); arrow1.fill.fore_color.rgb = BLUE; arrow1.line.fill.background()
arrow2 = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left_x + 5.7), Inches(2.7), Inches(0.8), Inches(0.2)); arrow2.fill.solid(); arrow2.fill.fore_color.rgb = BLUE; arrow2.line.fill.background()
arrow3 = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left_x + 9.2), Inches(2.7), Inches(0.75), Inches(0.2)); arrow3.fill.solid(); arrow3.fill.fore_color.rgb = BLUE; arrow3.line.fill.background()

# below bullets
add_bullet_list(slide, [
    'Nuxt portal ใช้ useAuth() บันทึก session และตรวจสิทธิ์ด้วย permissions จาก JWT',
    'middleware/auth ป้องกัน route ที่ต้อง login ก่อนเข้าถึง',
    'server proxy ส่ง request ไปยัง backend โดยไม่ต้องเปิด CORS ใน environment dev',
    'API เลือกตรวจสอบสิทธิ์ตาม endpoint และ role/permission ที่รับมาจาก token'
], left=0.8, top=4.25, width=11.6, height=2.0)

# Slide 3 flow
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'Flow การทำงานแบบ step-by-step', 'Login → session validation → API call → refresh on 401')
steps = [
    ('1\nLogin', 'POST /api/auth/login\nรับ accessToken และ refreshToken'),
    ('2\nPersist', 'เก็บ session หลักใน Auth Store\nและ localStorage'),
    ('3\nRoute Guard', 'middleware/auth ตรวจ session\nถ้าไม่มี redirect /login'),
    ('4\nSecure Request', 'auth.request() ใส่ Bearer token\nส่งไปยัง API พร้อม permission'),
    ('5\nAuto Retry', 'ถ้า 401 -> refresh token\nretry request หรือ logout หาก fail')
]
left_start = 0.65
for idx, (label, desc) in enumerate(steps):
    x = left_start + idx * 2.2
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.0), Inches(1.9), Inches(2.6))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE; box.line.color.rgb = BLUE; box.line.width = Pt(1.4)
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = label; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(17); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.text = desc; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(10.5); p2.runs[0].font.color.rgb = TEXT
    if idx < len(steps)-1:
        arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 1.9), Inches(2.95), Inches(0.2), Inches(0.45)); arr.fill.solid(); arr.fill.fore_color.rgb = BLUE; arr.line.fill.background()

# Slide 4
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'ฟังก์ชันหลักในโค้ด', 'ชิ้นส่วนสำคัญที่ทำให้ระบบทำงานได้')
add_bullet_list(slide, [
    'composables/useAuth.ts: ทำหน้าที่ central auth layer สำหรับ login, refresh, logout, request API และ permission check',
    'utils/auth.ts: normalize token response จาก API เพื่อรองรับทั้งรูปแบบ camelCase และ PascalCase',
    'server/routes/backend/[...path].ts: proxy path ไปยัง API backend ของ .NET โดยไม่ต้องตั้ง CORS ตอน dev',
    'middleware/auth.ts: ป้องกัน route ที่ต้องการ login ก่อนเข้าถึง',
    'components/PermissionGate.vue: ควบคุมการแสดงผลหรือการปิดใช้งาน UI ตาม permission ของผู้ใช้',
    'pages/abatement.vue: ทดสอบ permission-based API call สำหรับ read/create/update/delete/approve'
], left=0.8, top=1.5, width=11.5, height=5.1)

# Slide 5
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'หน้าจอหลักและความสัมพันธ์กับสิทธิ์', 'แต่ละหน้าแสดงตาม permission ที่ได้รับจาก token')
add_bullet_list(slide, [
    'Login page: เข้าสู่ระบบด้วย username และ password',
    'Overview dashboard: แสดงสรุปสิทธิ์, roles, token expiry และ session status',
    'Abatement page: ทดสอบ permission-based API call ตาม action ที่ user มีสิทธิ์',
    'Permissions page: prototype สำหรับจัดการ role-to-permission matrix',
    'Users page: prototype สำหรับการดู/จัดการ user และ role assignment',
    'Sessions page: ดูเซสชันที่ใช้งานอยู่และ revoke session ได้'
], left=0.8, top=1.5, width=11.5, height=5.0)

# Slide 6
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'กลไก RBAC ที่ถูกบังคับใช้จริง', 'Permission ถูกประเมินจาก session และ route')
blocks = [
    ('👥\nRole', 'ADMIN / APPROVER / USER'),
    ('🔐\nPermission', 'abatement.read, role.manage, user.manage, ...'),
    ('🧱\nPermissionGate', 'เงื่อนไขตรวจสิทธิ์ก่อน render หรือ enable action'),
    ('🧭\nNavigation', 'เมนูที่ไม่ได้รับสิทธิ์จะถูกซ่อนหรือปิดใช้งาน')
]
for idx, (label, text) in enumerate(blocks):
    x = 0.8 + idx*3.0
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.1), Inches(2.5), Inches(2.25))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.color.rgb = BORDER; box.line.width = Pt(1)
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = label; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(18); p.runs[0].font.bold=True; p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.text = text; p2.runs[0].font.name='Kanit'; p2.runs[0].font.size=Pt(11); p2.runs[0].font.color.rgb = TEXT

# Slide 7 final summary
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = NAVY
add_title(slide, 'สรุป', 'สิ่งที่โปรเจกต์นี้ให้ทีมเห็นชัดเจน')
box = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.7), Inches(3.6))
tf = box.text_frame
for idx, text in enumerate([
    'โปรเจกต์นี้เป็น Frontend หลักสำหรับบริหาร JWT และ RBAC ของ AccessFlow',
    'ทีมสามารถตรวจสอบ session, user permission, และ route access ได้จาก portal ได้ตรงจุด',
    'โครงสร้างของระบบถูกออกแบบให้แยก rõ ระหว่าง presentation layer, auth layer, proxy layer, และ backend service',
    'พร้อมต่อยอดไปสู่ user/role admin management และ audit workflow ในอนาคต'
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph(); p.text = text; p.bullet = True; p.runs[0].font.name='Kanit'; p.runs[0].font.size=Pt(22 if idx < 2 else 20); p.runs[0].font.color.rgb = WHITE; p.space_after = Pt(10)

output = r'C:\Users\TIUM VSM\source\repos\WebAPI_DOTNET10\web-portal\AccessFlow-RBAC-Overview.pptx'
prs.save(output)
print('Saved to:', output)
print('Slides:', len(prs.slides))
