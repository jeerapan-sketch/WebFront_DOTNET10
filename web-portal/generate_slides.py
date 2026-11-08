from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

NAVY = RGBColor(16, 36, 62)
BLUE = RGBColor(25, 118, 210)
LIGHT = RGBColor(244, 247, 250)
TEXT = RGBColor(24, 40, 59)
MUTED = RGBColor(111, 126, 143)
WHITE = RGBColor(255, 255, 255)
BORDER = RGBColor(228, 234, 240)


def add_title(slide, title, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(11.5), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.runs[0].font.size = Pt(26)
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = NAVY
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.72), Inches(0.95), Inches(10.5), Inches(0.4))
        st = sub_box.text_frame
        p2 = st.paragraphs[0]
        p2.text = subtitle
        p2.runs[0].font.size = Pt(12)
        p2.runs[0].font.color.rgb = MUTED


def add_bullets(slide, bullets, left=0.8, top=1.5, width=11.4, height=5.0, font_size=18):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = b
        p.level = 0
        p.bullet = True
        p.space_after = Pt(7)
        p.runs[0].font.size = Pt(font_size)
        p.runs[0].font.color.rgb = TEXT

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = LIGHT
bar = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(13.33), Inches(0.45))
bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
logo = slide.shapes.add_shape(1, Inches(0.7), Inches(0.8), Inches(0.9), Inches(0.9))
logo.fill.solid(); logo.fill.fore_color.rgb = BLUE; logo.line.fill.background(); logo.text = 'A'
logo.text_frame.paragraphs[0].runs[0].font.bold = True
logo.text_frame.paragraphs[0].runs[0].font.size = Pt(25)
logo.text_frame.paragraphs[0].runs[0].font.color.rgb = WHITE

box = slide.shapes.add_textbox(Inches(1.95), Inches(0.85), Inches(6.1), Inches(1.0))
tf = box.text_frame
p = tf.paragraphs[0]
p.text = 'AccessFlow RBAC Portal'
p.runs[0].font.size = Pt(30)
p.runs[0].font.bold = True
p.runs[0].font.color.rgb = NAVY
p2 = tf.add_paragraph(); p2.text = 'Project overview for engineering team'; p2.runs[0].font.size = Pt(15); p2.runs[0].font.color.rgb = MUTED

info = slide.shapes.add_shape(1, Inches(9.1), Inches(0.9), Inches(3.2), Inches(2.9))
info.fill.solid(); info.fill.fore_color.rgb = WHITE; info.line.color.rgb = BORDER; info.line.width = Pt(1.2)
info.text = 'Nuxt 3\nJWT + RBAC\nBackend Proxy\nFrontend portal'
for idx, paragraph in enumerate(info.text_frame.paragraphs):
    paragraph.runs[0].font.size = Pt(17 if idx == 0 else 12)
    paragraph.runs[0].font.bold = idx == 0
    paragraph.runs[0].font.color.rgb = NAVY if idx == 0 else MUTED

add_bullets(slide, [
    'Nuxt 3 portal สำหรับจัดการสิทธิ์การเข้าถึงและ session ของผู้ใช้งาน',
    'ใช้ JWT สำหรับ authenticate และ RBAC สำหรับ permission-based access control',
    'เรียก API ฝั่ง .NET ผ่าน proxy local เพื่อหลีกเลี่ยง CORS ตอน dev',
    'มีหน้า login, overview, abatement, permissions, users, sessions'
], left=0.8, top=3.2, width=7.6, height=2.7, font_size=18)

# Slide 2
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'Project Structure', 'Main folders and responsibilities')
add_bullets(slide, [
    'pages/: หน้าจอหลัก เช่น login, overview, abatement, permissions, users, sessions',
    'components/: UI layout เช่น AppShell และ PermissionGate',
    'composables/: auth logic ที่เรียก login, refresh, logout และ request API',
    'middleware/: route guard ตรวจ session ก่อนเปิดหน้าใด ๆ',
    'server/routes/backend/: reverse proxy ไปยัง backend API ที่ localhost:5109',
    'utils/auth.ts: normalize token response ให้รองรับ camelCase และ PascalCase',
    'types/auth.ts: define contract ของ session และ token',
    'tests/auth.test.ts: unit test สำหรับ session normalizer'
], left=0.8, top=1.5, width=11.5, height=5.0, font_size=18)

# Slide 3
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'Authentication Flow', 'Login -> restore session -> protected requests -> refresh on 401')
steps = [
    ('1. Login', 'เรียก /api/auth/login\nรับ accessToken + refreshToken'),
    ('2. Persist', 'เก็บ session ลง localStorage\nและ state ใน useAuth()'),
    ('3. Guard', 'middleware/auth ตรวจ session\nถ้าไม่มี redirect /login'),
    ('4. Request', 'auth.request() แนบ Bearer token\nส่งไปยัง backend ผ่าน proxy'),
    ('5. Refresh', 'เมื่อ 401 ให้ refresh token\nถ้า fail ให้ logout')
]
left_start = 0.7
for idx, (title, desc) in enumerate(steps):
    box = slide.shapes.add_shape(1, Inches(left_start + idx * 2.2), Inches(2.1), Inches(2.0), Inches(2.5))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE; box.line.color.rgb = BLUE; box.line.width = Pt(1.4)
    tf = box.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title; p.alignment = PP_ALIGN.CENTER; p.runs[0].font.bold = True; p.runs[0].font.size = Pt(17); p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.text = desc; p2.alignment = PP_ALIGN.CENTER; p2.runs[0].font.size = Pt(10.5); p2.runs[0].font.color.rgb = TEXT
    if idx < len(steps) - 1:
        arrow = slide.shapes.add_shape(1, Inches(left_start + idx * 2.2 + 1.95), Inches(2.8), Inches(0.2), Inches(0.5))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = BLUE; arrow.line.fill.background()

# Slide 4
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'Core Implementation', 'Key files and responsibilities')
add_bullets(slide, [
    'composables/useAuth.ts: login, refresh, logout, request API, ตรวจสิทธิ์ permission',
    'utils/auth.ts: normalize session จาก API รวมทั้งรูปแบบ camelCase และ PascalCase',
    'server/routes/backend/[...path].ts: proxy path ไปยัง API backend ของ .NET',
    'middleware/auth.ts: guard route และ redirect ไปหน้า login หากยังไม่ได้ login',
    'components/PermissionGate.vue: hide หรือ block การดำเนินการตามสิทธิ์ปัจจุบัน',
    'pages/abatement.vue: ทดสอบ permission-based API calls เช่น read/create/update/delete/approve'
], left=0.8, top=1.5, width=11.4, height=4.9, font_size=18)

# Slide 5
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'Main Screens', 'What the portal shows to users')
add_bullets(slide, [
    'Login page: ผู้ใช้กรอก username/password และเข้าสู่ระบบ',
    'Overview dashboard: แสดง permissions, roles, token expiry and summary',
    'Abatement page: ทดสอบ permission สำหรับการทำงานต่าง ๆ ตามสิทธิ์',
    'Permissions page: prototype สำหรับสร้าง/ดู Role และ Permission matrix',
    'Users page: prototype การจัดการผู้ใช้งานและ role assignment',
    'Sessions page: ดูเซสชันปัจจุบันและสามารถ revoke session ได้'
], left=0.8, top=1.5, width=11.2, height=5.0, font_size=18)

# Slide 6
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
add_title(slide, 'Access Control Model', 'Permissions are enforced by session + route checks')
blocks = [
    ('Role', 'ADMIN / APPROVER / USER'),
    ('Permission', 'abatement.read, role.manage, user.manage, ...'),
    ('UI Gate', 'PermissionGate ตรวจ permission จาก session'),
    ('Navigation', 'เมนูที่ไม่ได้รับสิทธิ์จะแสดงหรือถูกซ่อนอัตโนมัติ')
]
for idx, (title, text) in enumerate(blocks):
    box = slide.shapes.add_shape(1, Inches(0.8 + idx * 3.0), Inches(2.1), Inches(2.5), Inches(2.2))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT; box.line.color.rgb = BORDER; box.line.width = Pt(1)
    tf = box.text_frame; tf.clear()
    p = tf.paragraphs[0]; p.text = title; p.runs[0].font.bold = True; p.runs[0].font.size = Pt(18); p.runs[0].font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.text = text; p2.runs[0].font.size = Pt(12); p2.runs[0].font.color.rgb = TEXT

# Slide 7
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = LIGHT
add_title(slide, 'Deployment and Environment', 'Operational context')
add_bullets(slide, [
    'Nuxt app ใช้งานที่ http://localhost:3000 ใน environment dev',
    'API backend คาดหวังที่ http://localhost:5109',
    'runtimeConfig ทำ mapping ของ /backend/* ถึง apiProxyTarget',
    'Docker, Kind, Helm, Vault และ Jenkins deployment flow ถูกอธิบายใน README.md',
    'README.md ระบุ tag convention และ release pipeline สำหรับ dev/uat/prod'
], left=0.8, top=1.5, width=11.2, height=4.8, font_size=18)

# Slide 8
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.background.fill.solid(); slide.background.fill.fore_color.rgb = NAVY
add_title(slide, 'Summary', 'What this project is designed to do')
box = slide.shapes.add_textbox(Inches(0.9), Inches(1.8), Inches(11.8), Inches(3.3))
tf = box.text_frame
for idx, text in enumerate([
    'สร้าง frontend สำหรับบริหาร JWT และ RBAC ของ AccessFlow',
    'ให้ทีมตรวจสอบสิทธิ์ การเข้าถึง และ session ได้อย่างชัดเจนและมีความปลอดภัย',
    'เป็น portal ที่ต่อกับ API จริง และพร้อมขยายฟีเจอร์สำหรับ user/role admin CRUD ในอนาคต'
]):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = text
    p.bullet = True
    p.runs[0].font.size = Pt(22)
    p.runs[0].font.color.rgb = WHITE
    p.space_after = Pt(10)

output = r'C:\Users\TIUM VSM\source\repos\WebAPI_DOTNET10\web-portal\AccessFlow-RBAC-Overview.pptx'
prs.save(output)
print('Saved to:', output)
print('Slides:', len(prs.slides))
