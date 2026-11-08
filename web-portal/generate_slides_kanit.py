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
SOFT = RGBColor(235, 243, 255)
WHITE = RGBColor(255, 255, 255)
TEXT = RGBColor(33, 46, 63)
MUTED = RGBColor(103, 119, 136)
GREEN = RGBColor(20, 150, 111)
RED = RGBColor(200, 76, 76)
BORDER = RGBColor(222, 231, 239)


def set_font(run, size=18, bold=False, color=TEXT, name='Kanit'):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = name


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(9.8), Inches(0.85))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.alignment = PP_ALIGN.LEFT
    r = p.runs[0]
    set_font(r, size=26, bold=True, color=NAVY)
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.72), Inches(0.98), Inches(10.0), Inches(0.35))
        st = sub_box.text_frame
        p2 = st.paragraphs[0]
        p2.text = subtitle
        r2 = p2.runs[0]
        set_font(r2, size=11, color=MUTED)


def add_bullet_list(slide, items, left=0.8, top=1.6, width=11.3, height=5.0):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for idx, text in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = text
        p.level = 0
        p.bullet = True
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        r = p.runs[0]
        set_font(r, size=18, color=TEXT)


def add_icon_card(slide, x, y, w, h, icon, title, body, accent=BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = WHITE
    shape.line.color.rgb = BORDER
    shape.line.width = Pt(1.2)

    icon_box = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.14), Inches(0.62), Inches(0.5))
    it = icon_box.text_frame
    p = it.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.runs[0]
    r.text = icon
    r.font.size = Pt(24)
    r.font.name = 'Segoe UI Emoji'

    header = slide.shapes.add_textbox(Inches(x + 0.9), Inches(y + 0.12), Inches(w - 1.0), Inches(0.4))
    ht = header.text_frame
    p2 = ht.paragraphs[0]
    p2.text = title
    r2 = p2.runs[0]
    set_font(r2, size=17, bold=True, color=NAVY)

    body_box = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.62), Inches(w - 0.24), Inches(h - 0.74))
    bt = body_box.text_frame
    p3 = bt.paragraphs[0]
    p3.text = body
    r3 = p3.runs[0]
    set_font(r3, size=11, color=TEXT)

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT

bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.33), Inches(0.45))
bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()

logo = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(0.75), Inches(0.9), Inches(0.9))
logo.fill.solid(); logo.fill.fore_color.rgb = BLUE; logo.line.fill.background()
logo.text = 'A'
logo.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
logo.text_frame.paragraphs[0].runs[0].font.size = Pt(26)
logo.text_frame.paragraphs[0].runs[0].font.bold = True
logo.text_frame.paragraphs[0].runs[0].font.color.rgb = WHITE
logo.text_frame.paragraphs[0].runs[0].font.name = 'Kanit'

box = slide.shapes.add_textbox(Inches(1.9), Inches(0.8), Inches(7.5), Inches(1.0))
tf = box.text_frame
p = tf.paragraphs[0]; p.text = 'AccessFlow RBAC Portal'; p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(30); p.runs[0].font.bold = True; p.runs[0].font.color.rgb = NAVY
p2 = tf.add_paragraph(); p2.text = 'ภาพรวมระบบสำหรับทีมพัฒนา'; p2.runs[0].font.name = 'Kanit'; p2.runs[0].font.size = Pt(15); p2.runs[0].font.color.rgb = MUTED

# Info card
info = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.25), Inches(0.9), Inches(3.3), Inches(2.9))
info.fill.solid(); info.fill.fore_color.rgb = WHITE; info.line.color.rgb = BORDER; info.line.width = Pt(1.1)
info.text = 'Nuxt 3\nJWT + RBAC\nBackend Proxy\nFrontend portal'
info.text_frame.paragraphs[0].runs[0].font.name = 'Kanit'; info.text_frame.paragraphs[0].runs[0].font.size = Pt(18); info.text_frame.paragraphs[0].runs[0].font.bold = True; info.text_frame.paragraphs[0].runs[0].font.color.rgb = NAVY
for idx in range(1, len(info.text_frame.paragraphs)):
    info.text_frame.paragraphs[idx].runs[0].font.name = 'Kanit'
    info.text_frame.paragraphs[idx].runs[0].font.size = Pt(12)
    info.text_frame.paragraphs[idx].runs[0].font.color.rgb = MUTED

add_bullet_list(slide, [
    'เว็บแอปสำหรับจัดการสิทธิ์การเข้าถึงและ session ของผู้ใช้งาน',
    'ใช้ JWT เป็นช่องทางยืนยันตัวตนและ RBAC ควบคุมสิทธิ์ตามบทบาท',
    'เชื่อมต่อ API ฝั่ง .NET ผ่าน proxy local สำหรับสภาพแวดล้อม dev',
    'มีหน้า login, overview, abatement, permissions, users, sessions'
], left=0.8, top=3.25, width=7.6, height=2.5)

# right vertical icons
for idx, (icon, text) in enumerate([('🔐', 'Security'), ('🧩', 'RBAC'), ('🖥️', 'Portal'), ('📊', 'Audit')]):
    y = 3.2 + idx * 0.85
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.0), Inches(y), Inches(3.55), Inches(0.62))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE; box.line.color.rgb = BORDER
    tf = box.text_frame; tf.clear();
    p = tf.paragraphs[0]; p.text = f'{icon} {text}'; p.alignment = PP_ALIGN.LEFT; p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(12); p.runs[0].font.color.rgb = NAVY

# Slide 2
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'โครงสร้างโปรเจกต์', 'ระบบที่ถูกจัดกลุ่มตามหน้าที่ใช้งาน')
add_bullet_list(slide, [
    'pages/: หน้า UI หลัก เช่น login, overview, abatement, permissions, users, sessions',
    'components/: layout และ UI widget เช่น sidebar, PermissionGate',
    'composables/: logic ของ auth ทั้ง login, refresh, logout และ request API',
    'middleware/: guard route ก่อนเข้าหน้า เพื่อตรวจ session',
    'server/routes/backend/: proxy ไปยัง backend API ของ .NET',
    'utils/auth.ts: normalize token response ที่มาจาก API ทั้ง camelCase และ PascalCase',
    'types/auth.ts: define contract ของ session และ token',
    'tests/auth.test.ts: unit test ตรวจสอบความถูกต้องของ session normalization'
], left=0.8, top=1.5, width=11.8, height=5.0)

# Slide 3 Flow chart
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'Flow การทำงาน', 'Login → session → protected request → refresh token')

steps = [
    ('🔑\nเข้าสู่ระบบ', 'POST /api/auth/login\nรับ accessToken + refreshToken'),
    ('💾\nบันทึกเซสชัน', 'เก็บ session ลง localStorage\nและ state ภายใน useAuth()'),
    ('🛡️\nปกป้อง route', 'middleware/auth ตรวจ session\nถ้าไม่มีให้ redirect /login'),
    ('📡\nเรียก API', 'auth.request() แนบ Bearer token\nส่งไป backend ผ่าน proxy'),
    ('🔄\nรีเฟรช token', 'ถ้า 401 จะ refresh token\nถ้า fail จะ logout ทันที')
]
left_start = 0.7
for idx, (label, desc) in enumerate(steps):
    x = left_start + idx * 2.2
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.1), Inches(1.9), Inches(2.5))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE; box.line.color.rgb = BLUE; box.line.width = Pt(1.4)
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_VERTICAL_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = label; p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(18); p.runs[0].font.bold = True; p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.text = desc; p2.runs[0].font.name = 'Kanit'; p2.runs[0].font.size = Pt(10.5); p2.runs[0].font.color.rgb = TEXT
    if idx < len(steps)-1:
        arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 1.9), Inches(2.8), Inches(0.22), Inches(0.45))
        arr.fill.solid(); arr.fill.fore_color.rgb = BLUE; arr.line.fill.background()

# Slide 4
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'ฟังก์ชันหลักในระบบ', 'โค้ดที่ทำงานจริงของ auth และ permission control')
add_bullet_list(slide, [
    'composables/useAuth.ts: ทำหน้าที่ login, refresh token, logout, request API และตรวจสิทธิ์ permission',
    'utils/auth.ts: normalize session data ให้รองรับทั้งรูปแบบ camelCase และ PascalCase',
    'server/routes/backend/[...path].ts: proxy path ไปยัง backend API ฝั่ง .NET',
    'middleware/auth.ts: guard route และ redirect ไปหน้า login หากไม่มี session',
    'components/PermissionGate.vue: ซ่อนหรือปิดใช้งาน action ตามสิทธิ์ที่ user มี',
    'pages/abatement.vue: ทดสอบ permission-based API calls เช่น read/create/update/delete/approve'
], left=0.8, top=1.5, width=11.5, height=5.0)

# Slide 5
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'หน้าจอหลัก', 'สิ่งที่ผู้ใช้เห็นใน portal')
add_bullet_list(slide, [
    'Login page: ผู้ใช้กรอก username/password เพื่อเข้าสู่ระบบ',
    'Overview dashboard: แสดงสิทธิ์ ปริมาณ role และเวลาหมดอายุของ token',
    'Abatement page: ทดสอบการเรียก API ตาม permission เช่น read, create, update, approve, delete',
    'Permissions page: prototype สำหรับจัดการ role-to-permission matrix',
    'Users page: prototype การจัดการผู้ใช้งานและ role assignment',
    'Sessions page: ดู session ที่กำลังใช้งานและสามารถ revoke session ได้'
], left=0.8, top=1.5, width=11.5, height=5.0)

# Slide 6
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'รูปแบบการควบคุมสิทธิ์', 'permission ถูกตรวจจาก session ที่ login แล้ว')
blocks = [
    ('👥\nRole', 'ADMIN / APPROVER / USER'),
    ('🔐\nPermission', 'abatement.read, role.manage, user.manage, ...'),
    ('🧱\nGate', 'PermissionGate ตรวจสิทธิ์จาก session'),
    ('🧭\nNavigation', 'เมนูและ action ถูกซ่อนหรือปิดใช้งานอัตโนมัติ')
]
for idx, (label, text) in enumerate(blocks):
    x = 0.8 + idx * 3.0
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.1), Inches(2.5), Inches(2.25))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.color.rgb = BORDER; box.line.width = Pt(1)
    tf = box.text_frame; tf.word_wrap = True; tf.clear()
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.text = label; p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(18); p.runs[0].font.bold = True; p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER; p2.text = text; p2.runs[0].font.name = 'Kanit'; p2.runs[0].font.size = Pt(11); p2.runs[0].font.color.rgb = TEXT

# Slide 7 Summary
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = NAVY
add_title(slide, 'สรุป', 'สิ่งที่โปรเจกต์นี้ทำให้ทีมเห็นชัดเจน')
box = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.6), Inches(3.4))
tf = box.text_frame
for idx, text in enumerate([
    'ระบบนี้ทำหน้าที่เป็น Frontend สำหรับบริหาร JWT และ RBAC ของ AccessFlow',
    'ช่วยให้ทีมเห็นสถานะ session และสิทธิ์ที่ใช้ควบคุมการเข้าถึงได้แบบชัดเจน',
    'พร้อมขยายฟีเจอร์ user/role management และ audit ต่อไปได้ในอนาคต'
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.bullet = True
    p.runs[0].font.name = 'Kanit'; p.runs[0].font.size = Pt(23); p.runs[0].font.color.rgb = WHITE; p.space_after = Pt(10)

output = r'C:\Users\TIUM VSM\source\repos\WebAPI_DOTNET10\web-portal\AccessFlow-RBAC-Overview.pptx'
prs.save(output)
print('Saved to:', output)
print('Slides:', len(prs.slides))
