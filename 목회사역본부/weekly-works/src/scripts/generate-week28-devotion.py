from __future__ import annotations

import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".claude/skills/weekly-devotion/templates"
DATA_PATH = ROOT / ".claude/skills/weekly-devotion/devotion-data.json"
OUT = ROOT / "output/7월/2주차/매일묵상"
HTML_OUT = OUT / "html-original"


EXPECTED_WEEK28 = {
    "month": "7월",
    "start_date": "07-13",
    "mon": "갈 6:1-2",
    "tue": "눅 10:33-37",
    "wed": "요 13:14-17",
    "thu": "빌 2:4-7",
    "fri": "시 133:1",
}


ADULT_WORDPRESS_TEMPLATE = """<article style="font-family:'Noto Serif KR','Nanum Myeongjo',serif;background:#fdfaf5;color:#2f261d;max-width:780px;margin:0 auto;padding:2.2rem;line-height:1.85;">
  <header style="text-align:center;border-bottom:2px solid #d8c7aa;padding-bottom:1.5rem;margin-bottom:1.8rem;">
    <h1 class="qt-title" style="color:#5e3d1b;font-size:2rem;margin:0 0 .6rem;">{제목}</h1>
    <p class="qt-date" style="color:#7a684f;margin:0;">{월}월 {일}일 {요일}요일 | {성경_구절_위치}</p>
    <p style="margin:1.2rem 0 0;"><a href="[이미지_원본_URL]" target="_blank"><img src="[이미지_URL]" alt="Meditation Image" style="width:100%;max-width:680px;border-radius:8px;" /></a></p>
  </header>
  <section class="qt-scripture" style="margin-top:1.8rem;">
    <h2 style="color:#5e3d1b;font-size:1.25rem;">본문 말씀</h2>
    <blockquote style="background:#fbf3e6;border-left:4px solid #b58b54;margin:0;padding:1rem 1.2rem;white-space:pre-line;">{성경_본문_전체}</blockquote>
    <p style="text-align:right;color:#7a684f;">({성경_구절_위치}, 개역개정)</p>
  </section>
  <section class="qt-reflection" style="margin-top:1.8rem;">
    <h2 style="color:#5e3d1b;font-size:1.25rem;">본문 해석 및 적용</h2>
    {해설_단락들_p태그포함}
  </section>
  <section class="qt-questions" style="margin-top:1.8rem;">
    <h2 style="color:#5e3d1b;font-size:1.25rem;">묵상을 위한 질문</h2>
    <ol>
      <li>{질문1_본문이해}</li>
      <li>{질문2_내면성찰}</li>
      <li>{질문3_실천적용}</li>
    </ol>
  </section>
  <section class="qt-prayer" style="margin-top:1.8rem;background:#fbf3e6;padding:1.2rem;border-radius:8px;">
    <h2 style="color:#5e3d1b;font-size:1.25rem;">오늘의 기도</h2>
    <p style="font-style:italic;white-space:pre-line;">{기도문_각_문장_줄바꿈}</p>
    <p style="text-align:right;font-weight:700;">예수님의 이름으로 기도합니다. 아멘.</p>
  </section>
  <footer class="qt-hashtags" style="margin-top:1.8rem;color:#7a684f;text-align:center;">#은혜누림 #서로세움 #디딤교회 {추가_해시태그}</footer>
</article>
"""


DAYS = [
    {
        "slug": "mon",
        "weekday": "월",
        "day_num": "13",
        "sot_key": "mon",
        "scripture_ref": "갈 6:1-2",
        "adult_title": "온유함으로 서로의 짐을 지는 공동체",
        "youth_title": "넘어진 친구를 세워 주는 믿음",
        "adult_scripture": "형제들아 사람이 만일 무슨 범죄한 일이 드러나거든 신령한 너희는 온유한 심령으로 그러한 자를 바로잡고 너 자신을 살펴보아 너도 시험을 받을까 두려워하라\n너희가 짐을 서로 지라 그리하여 그리스도의 법을 성취하라",
        "youth_scripture": "형제자매 여러분, 누군가 잘못한 것이 드러나면 성령을 따라 사는 사람답게 부드러운 마음으로 바로잡아 주세요. 그리고 여러분 자신도 시험에 빠지지 않도록 조심하세요. 서로의 짐을 져 주세요. 그렇게 하는 것이 그리스도의 법을 이루는 길입니다.",
        "adult_reflection": [
            "바울은 공동체 안에서 누군가의 잘못이 드러날 때, 가장 먼저 정죄가 아니라 온유를 말합니다. 죄를 가볍게 여기라는 뜻이 아니라, 넘어진 사람을 다시 세우는 마음으로 다가가라는 뜻입니다. 우리의 본능은 판단하고 거리를 두는 쪽으로 기울지만, 복음은 상처 입은 지체를 회복의 자리로 초대합니다.",
            "온유는 약한 태도가 아니라 그리스도의 마음을 닮은 힘입니다. 예수님은 우리의 무너짐을 보시고도 밀어내지 않으셨고, 십자가에서 우리의 무거운 짐을 친히 지셨습니다. 그래서 성도는 다른 사람의 짐을 보며 우월감을 느끼는 사람이 아니라, 자기 연약함을 기억하며 함께 짐을 나누는 사람입니다.",
            "오늘 말씀은 공동체의 사랑이 말로만 머물지 않게 합니다. 누군가의 아픔과 책임을 함께 들어 주고, 조심스럽고 따뜻한 말로 회복을 돕는 것이 그리스도의 법을 이루는 길입니다. 한 주의 시작에 하나님은 우리를 서로의 짐을 나누는 은혜의 통로로 부르십니다.",
        ],
        "adult_quote": "서로의 짐을 지는 사랑은 복음이 공동체 안에서 보이는 모양입니다.",
        "adult_questions": [
            "나는 누군가의 연약함을 볼 때 온유함보다 판단이 먼저 나오지는 않습니까?",
            "내가 지금 혼자 지고 있는 짐, 또는 함께 져 주어야 할 이웃의 짐은 무엇입니까?",
            "오늘 한 사람을 세워 주기 위해 건넬 수 있는 구체적인 말이나 행동은 무엇입니까?",
        ],
        "adult_prayer": "주님, 다른 사람의 연약함을 쉽게 판단하던 제 마음을 불쌍히 여겨 주소서. 저를 온유한 심령으로 빚으시고, 예수님께서 제 짐을 지신 은혜를 기억하며 누군가의 짐을 함께 나누게 하소서.",
        "adult_tags": "#갈라디아서 #온유 #서로짐을지라 #공동체회복 #월요일묵상",
        "youth_reflection": [
            "친구가 실수했을 때 우리는 쉽게 뒤에서 말하거나 마음속으로 점수를 매겨요. 그런데 바울은 <strong>넘어진 사람을 온유하게 세워 주라</strong>고 말해요. 잘못을 모른 척하라는 뜻이 아니라, 사람을 무너뜨리는 방식이 아니라 살리는 방식으로 다가가라는 뜻이에요.",
            "예수님은 우리가 넘어졌을 때 버려두지 않으셨어요. 우리의 죄와 부끄러움을 십자가에서 대신 지시고 다시 일어날 길을 열어 주셨어요. 그래서 믿음은 친구의 약점을 보고 우쭐해지는 마음이 아니라, '나도 은혜가 필요한 사람이야'라고 기억하는 마음에서 시작돼요.",
            "오늘 누군가 힘들어 보이면 그냥 지나치지 말아 보세요. 짧은 안부, 조용한 응원, 같이 들어 주는 시간도 짐을 나누는 방법이에요. 학교와 집에서 작은 배려를 시작할 때, 우리 공동체는 더 따뜻해질 수 있어요.",
        ],
        "youth_quote": "핵심 메시지: 믿음은 넘어진 사람을 세워 주는 사랑이야.",
        "youth_questions": [
            "친구의 실수를 봤을 때 나는 보통 어떻게 반응하나요?",
            "내가 요즘 혼자 지고 있는 짐은 무엇인가요?",
            "오늘 한 사람의 짐을 가볍게 해 줄 작은 행동은 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 친구의 약점을 보면 쉽게 판단할 때가 있어요. 오늘은 부드러운 마음으로 사람을 세워 주게 해 주세요. 제 짐도 주님께 맡기고, 다른 사람의 짐도 함께 들어 줄 용기를 주세요.",
        "youth_tags": "#청소년QT #서로짐을지라 #월요일QT #온유한마음 #친구세우기",
        "adult_kakao": [
            "📖 오늘의 묵상 | 7월 13일 월요일",
            "",
            "\"너희가 짐을 서로 지라\"",
            "— 갈라디아서 6:2",
            "",
            "새 한 주를 시작하며 서로의 짐을 바라보는 마음을 돌아봅니다.",
            "복음은 판단보다 회복을, 거리두기보다 함께 짐지는 사랑을 가르칩니다.",
            "오늘 한 사람의 짐을 조금 가볍게 하는 묵상으로 시작해요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 7월 13일 월요일",
            "",
            "\"서로의 짐을 져 주세요\"",
            "— 갈라디아서 6:2",
            "",
            "친구가 넘어졌을 때 웃는 사람보다 손 내미는 사람이 멋있어.",
            "오늘은 누군가의 마음을 조금 가볍게 해 주는 하루를 살아 보자.",
            "월요일 QT로 온유한 마음을 시작해!",
            "",
            "#청소년QT #디딤교회청소년 #오늘도말씀",
        ],
        "image_theme": "서로의 짐을 나누는 온유",
        "style_ref": "style3.png",
        "mj": "A quiet hand-painted watercolor scene of two travelers sharing one heavy bundle on a gentle dirt path, warm morning light, muted cream, olive, and dusty blue palette, visible paper texture, generous negative space, tender restoration and burden-bearing mood, NOT photorealistic, NOT glossy AI illustration --ar 16:9 --v 7",
        "gpt": "Use src/Image_style_refernence/style3.png as the style reference. Create a wide landscape composition of two simple travelers sharing one heavy bundle on a quiet path, with warm morning light, muted earth tones, soft watercolor and gouache texture, generous negative space, contemplative and tender. NOT photorealistic, NOT glossy AI illustration, no gradients. 16:9 horizontal (landscape) format.",
    },
    {
        "slug": "tue",
        "weekday": "화",
        "day_num": "14",
        "sot_key": "tue",
        "scripture_ref": "눅 10:33-37",
        "adult_title": "멈춰 서는 긍휼이 이웃을 만듭니다",
        "youth_title": "그냥 지나치지 않는 사람",
        "adult_scripture": "어떤 사마리아 사람은 여행하는 중 거기 이르러 그를 보고 불쌍히 여겨 가까이 가서 기름과 포도주를 그 상처에 붓고 싸매고 자기 짐승에 태워 주막으로 데리고 가서 돌보아 주니라\n그 이튿날 그가 주막 주인에게 데나리온 둘을 내어 주며 이르되 이 사람을 돌보아 주라 비용이 더 들면 내가 돌아올 때에 갚으리라 하였으니\n네 생각에는 이 세 사람 중에 누가 강도 만난 자의 이웃이 되겠느냐 이르되 자비를 베푼 자니이다 예수께서 이르시되 가서 너도 이와 같이 하라 하시니라",
        "youth_scripture": "한 사마리아 사람이 여행하다가 그 사람을 보고 불쌍한 마음이 들었습니다. 그는 가까이 가서 상처를 싸매 주고, 자기 짐승에 태워 여관으로 데려가 돌보아 주었습니다. 예수님은 자비를 베푼 사람이 참된 이웃이라고 말씀하시며, 너도 가서 그렇게 하라고 하셨습니다.",
        "adult_reflection": [
            "예수님의 비유에서 사마리아 사람은 길가에 쓰러진 사람을 보고 멈춰 섭니다. 그는 상황을 분석하는 데서 끝나지 않고 가까이 가며, 상처를 싸매고, 자기 자원을 사용해 돌봅니다. 이웃은 단지 가까이 사는 사람이 아니라 긍휼 때문에 멈춰 서는 사람입니다.",
            "우리는 바쁨과 피로를 이유로 누군가의 고통을 지나칠 때가 많습니다. 그러나 주님은 우리를 보시고 지나치지 않으셨습니다. 죄와 상처 가운데 쓰러진 우리에게 가까이 오셔서, 자신의 생명으로 우리를 살리셨습니다. 선한 사마리아인의 긍휼은 결국 우리에게 먼저 임한 그리스도의 긍휼을 비춥니다.",
            "오늘 말씀은 사랑을 감정이 아니라 방향 전환으로 보여 줍니다. 내 일정만 향하던 발걸음을 잠시 멈추고, 도움이 필요한 사람에게 가까이 가는 선택이 이웃 사랑의 시작입니다. 하나님은 작은 자비의 행동을 통해 우리의 길 위에 복음의 향기를 남기십니다.",
        ],
        "adult_quote": "긍휼은 멀리서 안타까워하는 마음을 가까이 가는 사랑으로 바꿉니다.",
        "adult_questions": [
            "나는 어떤 사람의 어려움을 보면서도 바쁘다는 이유로 지나치고 있습니까?",
            "예수님께서 나에게 가까이 오신 긍휼은 오늘 내 마음을 어떻게 움직입니까?",
            "오늘 내가 가까이 가서 돌볼 수 있는 작은 필요는 무엇입니까?",
        ],
        "adult_prayer": "주님, 제 길만 보느라 이웃의 아픔을 지나쳤던 마음을 회개합니다. 저를 긍휼의 사람으로 새롭게 하시고, 예수님께서 제게 가까이 오신 은혜를 따라 오늘 도움이 필요한 이에게 가까이 가게 하소서.",
        "adult_tags": "#누가복음 #선한사마리아인 #긍휼 #이웃사랑 #화요일묵상",
        "youth_reflection": [
            "길가에 쓰러진 사람을 보고 그냥 지나간 사람들도 있었어요. 그런데 사마리아 사람은 멈춰 섰고, 가까이 갔고, 직접 도와줬어요. 예수님은 <strong>진짜 이웃은 자비를 베푸는 사람</strong>이라고 알려 주세요.",
            "학교에서도 비슷한 순간이 있어요. 혼자 있는 친구, 놀림받는 친구, 표정이 어두운 친구를 봤을 때 그냥 모른 척할 수 있죠. 하지만 예수님은 우리에게 먼저 가까이 오신 분이에요. 우리가 상처와 죄 가운데 있을 때 주님은 지나치지 않으셨어요.",
            "오늘은 누군가에게 먼저 다가가 보세요. 큰일이 아니어도 괜찮아요. 같이 앉아 주기, 말 걸어 주기, 도와줄 게 있는지 물어보기. 그 작은 멈춤이 누군가에게는 하나님의 사랑처럼 느껴질 수 있어요.",
        ],
        "youth_quote": "핵심 메시지: 이웃 사랑은 그냥 지나치지 않는 거야.",
        "youth_questions": [
            "나는 도움이 필요한 친구를 보고도 모른 척한 적이 있나요?",
            "예수님이 나를 지나치지 않으셨다는 사실은 어떤 위로가 되나요?",
            "오늘 내가 먼저 다가갈 수 있는 사람은 누구인가요?",
        ],
        "youth_prayer": "예수님, 도움이 필요한 사람을 보고도 귀찮아서 지나칠 때가 있어요. 오늘은 제 마음에 긍휼을 주세요. 작은 말과 행동으로 누군가에게 가까이 가는 사람이 되게 해 주세요.",
        "youth_tags": "#청소년QT #선한사마리아인 #화요일QT #그냥지나치지않기 #이웃사랑",
        "adult_kakao": [
            "📖 오늘의 묵상 | 7월 14일 화요일",
            "",
            "\"그를 보고 불쌍히 여겨 가까이 가서\"",
            "— 누가복음 10:33-34",
            "",
            "긍휼은 마음속 안타까움에서 멈추지 않고 가까이 가게 합니다.",
            "주님이 우리에게 가까이 오신 은혜가 오늘 우리의 발걸음을 바꿉니다.",
            "화요일, 그냥 지나치지 않는 이웃 사랑을 묵상해요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 7월 14일 화요일",
            "",
            "\"그는 가까이 가서 상처를 싸매 주었습니다\"",
            "— 누가복음 10:34",
            "",
            "진짜 이웃은 멀리서 보기만 하는 사람이 아니야.",
            "오늘은 혼자 있는 친구에게 먼저 다가가 보자.",
            "작은 관심이 큰 위로가 될 수 있어!",
            "",
            "#청소년QT #디딤교회청소년 #오늘도말씀",
        ],
        "image_theme": "멈춰 서는 긍휼",
        "style_ref": "style2.png",
        "mj": "A hand-painted watercolor road at sunset, one traveler kneeling beside a wounded figure with a cloth and small oil jar, quiet compassion, muted gold, olive, cream, and dusty blue palette, visible paper texture, generous negative space, contemplative biblical kindness, NOT photorealistic --ar 16:9 --v 7",
        "gpt": "Use src/Image_style_refernence/style2.png as the style reference. Paint a wide road at sunset where one traveler has stopped to gently care for a wounded person, with a small cloth and oil jar nearby. Use muted gold, olive, cream, and dusty blue tones, visible paper texture, soft watercolor/gouache, spacious composition, contemplative compassion. NOT photorealistic, NOT glossy AI illustration. 16:9 horizontal (landscape) format.",
    },
    {
        "slug": "wed",
        "weekday": "수",
        "day_num": "15",
        "sot_key": "wed",
        "scripture_ref": "요 13:14-17",
        "adult_title": "주님이 보이신 낮은 자리의 복",
        "youth_title": "예수님처럼 먼저 섬기기",
        "adult_scripture": "내가 주와 또는 선생이 되어 너희 발을 씻었으니 너희도 서로 발을 씻어 주는 것이 옳으니라\n내가 너희에게 행한 것 같이 너희도 행하게 하려 하여 본을 보였노라\n내가 진실로 진실로 너희에게 이르노니 종이 주인보다 크지 못하고 보냄을 받은 자가 보낸 자보다 크지 못하나니\n너희가 이것을 알고 행하면 복이 있으리라",
        "youth_scripture": "내가 주님이며 선생인데 너희 발을 씻어 주었으니, 너희도 서로 발을 씻어 주는 것이 옳다. 내가 너희에게 본을 보인 것은 너희도 내가 한 것처럼 하게 하려는 것이다. 이것을 알고 실천하면 복이 있다.",
        "adult_reflection": [
            "예수님은 제자들의 발을 씻기신 뒤, 그 행동을 단순한 감동적인 장면으로 남기지 않으셨습니다. 주와 선생이신 분이 낮은 종의 자리에 서셨으니, 제자들도 서로를 섬기는 길로 부름받았다고 말씀하십니다. 복음은 섬김을 말로 설명하기 전에 몸으로 보여 주신 주님의 본에서 시작됩니다.",
            "우리는 높아지고 인정받는 자리를 복으로 생각하기 쉽습니다. 그러나 예수님은 낮아지는 자리에 참된 복이 있음을 보여 주셨습니다. 그분은 제자들의 더러움을 만지셨고, 십자가에서 우리의 죄까지 담당하셨습니다. 그러므로 성도의 섬김은 자기 의를 드러내는 봉사가 아니라, 먼저 섬김 받은 은혜에 대한 응답입니다.",
            "오늘 말씀은 알고 끝나는 믿음이 아니라 행하는 믿음으로 우리를 초대합니다. 가까운 사람의 필요를 알아차리고, 말없이 낮은 일을 감당하며, 주님의 본을 따라 서로를 씻어 주는 삶이 복된 삶입니다. 낮은 자리에서 시작되는 섬김 속에 예수님의 향기가 드러납니다.",
        ],
        "adult_quote": "예수님의 본은 낮아짐이 손해가 아니라 복의 길임을 보여 줍니다.",
        "adult_questions": [
            "나는 어떤 자리에서 섬김보다 인정받기를 더 원하고 있습니까?",
            "예수님께서 먼저 나를 섬기셨다는 사실이 오늘 내 태도를 어떻게 바꿉니까?",
            "오늘 내가 조용히 감당할 수 있는 낮은 자리의 섬김은 무엇입니까?",
        ],
        "adult_prayer": "주님, 높아지고 인정받고 싶은 마음을 내려놓게 하소서. 제 발을 씻기신 예수님의 은혜를 기억하며, 가까운 사람의 필요를 조용히 섬기게 하시고 낮은 자리에서 주님의 복을 누리게 하소서.",
        "adult_tags": "#요한복음 #발씻김 #섬김의본 #낮은자리 #수요일묵상",
        "youth_reflection": [
            "예수님은 선생님이신데 제자들의 발을 씻어 주셨어요. 그 시대에는 정말 낮은 사람이 하던 일이었는데, 예수님이 먼저 하신 거예요. 그리고 <strong>너희도 서로 이렇게 섬기라</strong>고 말씀하셨어요.",
            "우리는 보통 멋있어 보이는 일, 인정받는 일을 하고 싶어 해요. 하지만 예수님은 아무도 하고 싶어 하지 않는 낮은 일을 통해 사랑을 보여 주셨어요. 십자가도 마찬가지예요. 예수님은 우리를 살리시려고 가장 낮은 자리까지 내려오셨어요.",
            "오늘 집이나 학교에서 작은 섬김을 하나 해 보세요. 누가 시키기 전에 정리하기, 친구를 도와주기, 가족에게 먼저 따뜻하게 말하기. 티 나지 않는 섬김도 예수님을 닮아 가는 멋진 길이에요.",
        ],
        "youth_quote": "핵심 메시지: 예수님을 닮는 길은 먼저 섬기는 거야.",
        "youth_questions": [
            "나는 어떤 일을 너무 낮아 보인다고 피하고 있나요?",
            "예수님이 먼저 나를 섬기셨다는 말이 어떻게 느껴지나요?",
            "오늘 아무도 몰라도 해볼 수 있는 섬김 하나는 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 인정받는 일만 하고 싶을 때가 많아요. 오늘은 예수님처럼 먼저 섬기는 마음을 주세요. 작은 일도 기쁨으로 하고, 낮은 자리에서 사랑을 보여 주게 해 주세요.",
        "youth_tags": "#청소년QT #발씻김 #수요일QT #먼저섬기기 #예수님닮기",
        "adult_kakao": [
            "📖 오늘의 묵상 | 7월 15일 수요일",
            "",
            "\"내가 너희에게 행한 것 같이 너희도 행하게 하려 하여\"",
            "— 요한복음 13:15",
            "",
            "예수님은 섬김을 설명하시기 전에 먼저 보여 주셨습니다.",
            "낮은 자리에서 누군가를 섬기는 일은 손해가 아니라 주님의 복을 배우는 길입니다.",
            "오늘 주님의 본을 따라 조용한 섬김을 시작해요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 7월 15일 수요일",
            "",
            "\"내가 너희에게 본을 보였다\"",
            "— 요한복음 13:15",
            "",
            "예수님은 말로만 섬기라고 하지 않으셨어.",
            "먼저 낮은 자리에서 사랑을 보여 주셨어.",
            "오늘 우리도 작은 섬김 하나를 해 보자!",
            "",
            "#청소년QT #디딤교회청소년 #오늘도말씀",
        ],
        "image_theme": "낮은 자리의 섬김",
        "style_ref": "style5.png",
        "mj": "A reverent hand-painted watercolor scene of a simple basin, folded towel, and sandals on a quiet floor, warm lamplight, muted cream, olive, brown, and soft gold palette, visible paper texture, generous negative space, humble servant love, contemplative, NOT photorealistic --ar 16:9 --v 7",
        "gpt": "Use src/Image_style_refernence/style5.png as the style reference. Create a wide symbolic scene with a simple basin, folded towel, and sandals on a quiet floor, warm lamplight, muted cream, olive, brown, and soft gold palette. Soft watercolor/gouache painting, visible paper texture, generous negative space, humble and reverent. NOT photorealistic, NOT glossy AI illustration. 16:9 horizontal (landscape) format.",
    },
    {
        "slug": "thu",
        "weekday": "목",
        "day_num": "16",
        "sot_key": "thu",
        "scripture_ref": "빌 2:4-7",
        "adult_title": "자기를 비워 다른 이를 돌보는 마음",
        "youth_title": "내 중심에서 예수님 마음으로",
        "adult_scripture": "각각 자기 일을 돌볼뿐더러 또한 각각 다른 사람들의 일을 돌보아\n너희 안에 이 마음을 품으라 곧 그리스도 예수의 마음이니\n그는 근본 하나님의 본체시나 하나님과 동등됨을 취할 것으로 여기지 아니하시고\n오히려 자기를 비워 종의 형체를 가지사 사람들과 같이 되셨고",
        "youth_scripture": "자기 일만 돌아보지 말고 다른 사람의 일도 돌아보세요. 여러분 안에 그리스도 예수의 마음을 품으세요. 예수님은 하나님과 같은 분이셨지만 그것을 붙잡고 높아지려 하지 않으시고, 오히려 자신을 비워 종의 모습으로 오셨습니다.",
        "adult_reflection": [
            "바울은 성도에게 자기 일만이 아니라 다른 사람의 일도 돌아보라고 권합니다. 이는 자기 삶을 방치하라는 말이 아니라, 자기중심성에 갇힌 시야를 복음 안에서 넓히라는 초대입니다. 공동체는 각자가 자기 유익만 붙들 때 메마르지만, 서로의 필요를 살필 때 생명을 얻습니다.",
            "그 근거는 그리스도 예수의 마음입니다. 예수님은 높으신 분이셨지만 자신의 높음을 붙잡아 자기 유익으로 삼지 않으셨습니다. 오히려 자기를 비워 종의 형체를 입고 우리에게 오셨습니다. 우리가 다른 사람을 돌볼 수 있는 힘은 자기 의지가 아니라, 먼저 우리를 위해 낮아지신 주님의 은혜에서 나옵니다.",
            "오늘 말씀은 우리의 관심 방향을 조용히 돌려 세웁니다. 내 일정, 내 감정, 내 필요만 바라보던 마음이 예수님의 마음을 품을 때 이웃의 필요를 보기 시작합니다. 다른 사람의 일을 돌아보는 작은 선택 속에서 그리스도의 겸손이 우리 안에 살아 움직입니다.",
        ],
        "adult_quote": "그리스도의 마음은 나를 지우는 것이 아니라, 사랑으로 시야를 넓히는 은혜입니다.",
        "adult_questions": [
            "나는 요즘 내 일과 내 감정에만 지나치게 갇혀 있지는 않습니까?",
            "예수님께서 자기를 비워 나에게 오신 은혜는 어떤 위로와 도전을 줍니까?",
            "오늘 내가 실제로 돌아볼 수 있는 다른 사람의 필요는 무엇입니까?",
        ],
        "adult_prayer": "주님, 제 마음이 제 일과 제 유익에만 갇히지 않게 하소서. 자기를 비워 종의 모습으로 오신 예수님의 마음을 제 안에 품게 하시고, 오늘 다른 사람의 필요를 살피는 겸손한 사랑으로 살게 하소서.",
        "adult_tags": "#빌립보서 #그리스도의마음 #겸손 #타인돌봄 #목요일묵상",
        "youth_reflection": [
            "우리는 매일 내 일정, 내 성적, 내 기분, 내 메시지에 집중하며 살아가요. 그런데 바울은 <strong>자기 일만 보지 말고 다른 사람의 일도 돌아보라</strong>고 말해요. 믿음은 내 중심 화면을 조금 넓히는 일이에요.",
            "예수님은 하나님과 같은 분이셨지만 높은 자리만 붙잡지 않으셨어요. 우리를 살리시려고 낮아지셨고, 종의 모습으로 오셨어요. 그래서 다른 사람을 돌아보는 건 그냥 착한 일이 아니라 예수님의 마음을 닮아 가는 일이에요.",
            "오늘 주변을 한번 살펴보세요. 피곤해 보이는 가족, 혼자 있는 친구, 도움이 필요한 사람. 작은 배려 하나가 예수님의 마음을 보여 줄 수 있어요. 내 중심에서 예수님 마음으로 업데이트되는 하루가 되면 좋겠어요.",
        ],
        "youth_quote": "핵심 메시지: 예수님 마음은 내 시선을 옆 사람에게 열어 줘.",
        "youth_questions": [
            "나는 오늘 무엇에 가장 많이 신경 쓰고 있나요?",
            "예수님이 낮아지셨다는 사실은 내 관계를 어떻게 바꾸나요?",
            "오늘 내가 돌아볼 수 있는 가족이나 친구의 필요는 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 제 일만 크게 보일 때가 많아요. 오늘 제 마음을 넓혀 주세요. 예수님처럼 다른 사람의 필요를 보고, 작은 배려로 사랑을 보여 주게 해 주세요.",
        "youth_tags": "#청소년QT #빌립보서 #목요일QT #예수님마음 #다른사람돌아보기",
        "adult_kakao": [
            "📖 오늘의 묵상 | 7월 16일 목요일",
            "",
            "\"너희 안에 이 마음을 품으라 곧 그리스도 예수의 마음이니\"",
            "— 빌립보서 2:5",
            "",
            "복음은 내 일만 바라보던 시선을 이웃의 필요로 넓혀 줍니다.",
            "자기를 비워 우리에게 오신 예수님의 마음이 오늘 우리의 관계를 바꿉니다.",
            "목요일, 그리스도의 마음을 품는 묵상으로 함께해요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 7월 16일 목요일",
            "",
            "\"다른 사람의 일도 돌아보세요\"",
            "— 빌립보서 2:4",
            "",
            "내 일만 크게 보일 때 예수님 마음을 떠올려 봐.",
            "예수님은 우리를 위해 낮아지셨어.",
            "오늘 옆 사람의 필요를 한 번 살펴보자!",
            "",
            "#청소년QT #디딤교회청소년 #오늘도말씀",
        ],
        "image_theme": "자기를 비워 돌보는 마음",
        "style_ref": "style6.png",
        "mj": "A quiet hand-painted still life of an open book, an empty cup being offered, and a small sprout near a window, soft morning light, muted cream, olive, brown, and gentle blue palette, visible paper texture, spacious humility and care, contemplative devotional mood, NOT photorealistic --ar 16:9 --v 7",
        "gpt": "Use src/Image_style_refernence/style6.png as the style reference. Create a wide still-life scene with an open book, an empty cup being offered forward, and a small sprout by a window. Use muted cream, olive, brown, and soft blue tones, visible paper texture, soft watercolor/gouache painting, generous negative space, quiet humility and care. NOT photorealistic, no gradients. 16:9 horizontal (landscape) format.",
    },
    {
        "slug": "fri",
        "weekday": "금",
        "day_num": "17",
        "sot_key": "fri",
        "scripture_ref": "시 133:1",
        "adult_title": "함께 거하는 아름다움",
        "youth_title": "하나 되는 공동체가 아름다워",
        "adult_scripture": "보라 형제가 연합하여 동거함이 어찌 그리 선하고 아름다운고",
        "youth_scripture": "보세요, 형제자매가 하나 되어 함께 사는 것은 정말 좋고 아름다운 일입니다.",
        "adult_reflection": [
            "시편 133편은 형제가 연합하여 함께 거하는 모습을 선하고 아름답다고 노래합니다. 성경이 말하는 연합은 단순히 같은 공간에 있는 상태가 아닙니다. 서로의 차이를 지우는 획일성도 아닙니다. 하나님 안에서 서로를 받아들이고, 같은 은혜 아래 함께 머무는 관계의 아름다움입니다.",
            "공동체의 하나 됨은 인간의 성격이나 노력만으로 유지되지 않습니다. 우리는 쉽게 비교하고, 상처를 기억하며, 마음의 거리를 만듭니다. 그러나 그리스도께서 십자가로 하나님과 우리 사이의 막힌 담을 허무셨기에, 성도는 화해와 연합의 자리로 다시 초대받습니다. 하나 됨은 우리가 만들어 내는 성과가 아니라 복음이 우리 가운데 맺는 열매입니다.",
            "한 주의 끝에서 이 말씀은 우리의 관계를 다시 바라보게 합니다. 작은 양보, 먼저 건네는 화해의 말, 함께 기도하는 시간이 공동체를 선하고 아름답게 세웁니다. 하나님은 흩어진 마음을 은혜 안에서 모으시고, 함께 거하는 삶을 통해 세상에 복음의 아름다움을 드러내십니다.",
        ],
        "adult_quote": "하나 됨은 같아지는 일이 아니라, 같은 은혜 안에 함께 머무는 일입니다.",
        "adult_questions": [
            "나는 공동체 안에서 어떤 이유로 마음의 거리를 만들고 있습니까?",
            "그리스도께서 나를 화해의 자리로 부르신다는 사실은 어떤 관계를 떠올리게 합니까?",
            "오늘 공동체의 하나 됨을 위해 내가 먼저 할 수 있는 작은 행동은 무엇입니까?",
        ],
        "adult_prayer": "하나님, 제 안의 비교와 서운함을 주님 앞에 내려놓습니다. 그리스도 안에서 우리를 하나 되게 하신 은혜를 기억하게 하시고, 제가 속한 가정과 교회와 공동체 안에 선하고 아름다운 연합을 이루게 하소서.",
        "adult_tags": "#시편 #연합 #하나됨 #공동체 #금요일묵상",
        "youth_reflection": [
            "시편은 형제자매가 하나 되어 함께 사는 것이 정말 좋고 아름답다고 말해요. 하나 된다는 건 모두가 똑같아지는 게 아니에요. 서로 다르지만 하나님 안에서 함께 걸어가는 거예요. <strong>하나님은 함께하는 공동체를 아름답게 보세요.</strong>",
            "우리는 친구 사이에서도 쉽게 갈라져요. 말 한마디에 서운해지고, 비교하고, 편을 나눌 때도 있어요. 그런데 예수님은 우리를 하나님과 화해시키려고 십자가를 지셨어요. 그 은혜를 알면 우리도 화해와 하나 됨을 포기하지 않을 수 있어요.",
            "금요일, 이번 주 관계를 돌아보세요. 먼저 미안하다고 말할 사람, 고맙다고 말할 사람, 함께 기도하고 싶은 사람이 있나요? 작은 화해와 따뜻한 말이 공동체를 정말 아름답게 만들 수 있어요.",
        ],
        "youth_quote": "핵심 메시지: 하나 됨은 하나님이 기뻐하시는 아름다운 모습이야.",
        "youth_questions": [
            "나는 친구나 가족과 마음의 거리를 두고 있지는 않나요?",
            "예수님이 화해를 이루셨다는 말은 내 관계에 어떤 의미가 있나요?",
            "오늘 하나 됨을 위해 먼저 건넬 수 있는 말은 무엇인가요?",
        ],
        "youth_prayer": "하나님, 저는 서운하면 마음을 닫을 때가 많아요. 오늘 제 마음을 부드럽게 해 주세요. 친구와 가족, 교회 공동체 안에서 먼저 화해하고 함께하는 사람이 되게 해 주세요.",
        "youth_tags": "#청소년QT #시편 #금요일QT #하나됨 #공동체사랑",
        "adult_kakao": [
            "📖 오늘의 묵상 | 7월 17일 금요일",
            "",
            "\"형제가 연합하여 동거함이 어찌 그리 선하고 아름다운고\"",
            "— 시편 133:1",
            "",
            "하나 됨은 같은 성향이 되는 것이 아니라 같은 은혜 안에 함께 머무는 일입니다.",
            "한 주의 끝에서 주님이 주시는 화해와 연합의 아름다움을 묵상합니다.",
            "오늘 먼저 건네는 따뜻한 말로 공동체를 세워요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 7월 17일 금요일",
            "",
            "\"하나 되어 함께 사는 것은 정말 아름다운 일입니다\"",
            "— 시편 133:1",
            "",
            "친구와 가족, 교회 안에서 하나 되는 건 하나님이 기뻐하시는 모습이야.",
            "오늘 먼저 고맙다, 미안하다, 같이하자고 말해 보자.",
            "작은 화해가 공동체를 아름답게 해!",
            "",
            "#청소년QT #디딤교회청소년 #오늘도말씀",
        ],
        "image_theme": "함께 거하는 아름다움",
        "style_ref": "style1.png",
        "mj": "A contemplative hand-painted watercolor still life of several small candles sharing one warm flame around a simple clay bowl, muted cream, olive, brown, and soft gold palette, visible paper texture, generous negative space, peaceful unity and shared dwelling, devotional, NOT photorealistic --ar 16:9 --v 7",
        "gpt": "Use src/Image_style_refernence/style1.png as the style reference. Create a wide contemplative still life of several small candles sharing one warm flame around a simple clay bowl, symbolizing unity and shared dwelling. Muted cream, olive, brown, and soft gold palette, visible paper texture, watercolor/gouache hand-painted style, generous negative space, peaceful and reverent. NOT photorealistic. 16:9 horizontal (landscape) format.",
    },
]


def read_text_with_retry(path: Path, attempts: int = 5) -> str:
    last: OSError | None = None
    for _ in range(attempts):
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            last = exc
            time.sleep(6)
    assert last is not None
    raise last


def load_template(name: str) -> str:
    if name == "adult-wordpress.html":
        try:
            return read_text_with_retry(TEMPLATES / name)
        except OSError:
            return ADULT_WORDPRESS_TEMPLATE
    return read_text_with_retry(TEMPLATES / name)


def replace_many(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace("{" + key + "}", value)
    return text


def p_tags(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def sentence_lines(text: str) -> str:
    return "\n".join(part.strip() for part in text.split(". ") if part.strip())


def validate_sot() -> None:
    data = json.loads(read_text_with_retry(DATA_PATH))
    week28 = data["weeks"]["28"]
    for key, expected in EXPECTED_WEEK28.items():
        actual = week28.get(key)
        if actual != expected:
            raise ValueError(f"week28 SOT mismatch: {key} expected {expected!r}, got {actual!r}")
    for entry in DAYS:
        actual = week28[entry["sot_key"]]
        if actual != entry["scripture_ref"]:
            raise ValueError(f"{entry['slug']} scripture mismatch: {actual} != {entry['scripture_ref']}")


def render() -> None:
    validate_sot()
    HTML_OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    (OUT / "html-with-images").mkdir(parents=True, exist_ok=True)
    (OUT / "captured").mkdir(parents=True, exist_ok=True)

    adult_wordpress = load_template("adult-wordpress.html")
    adult_a4 = load_template("adult-a4.html")
    youth_a4 = load_template("youth-a4.html")

    adult_msgs = [
        "# 28주차 매일묵상 카카오톡 동기부여 메시지 (장년용)",
        "생성일: 2026-07-07",
        "주간 기준: 2026-07-13~2026-07-17",
        "SOT: .claude/skills/weekly-devotion/devotion-data.json week 28",
        "",
        "---",
        "",
    ]
    youth_msgs = [
        "# 28주차 매일묵상 카카오톡 동기부여 메시지 (청소년용)",
        "생성일: 2026-07-07",
        "주간 기준: 2026-07-13~2026-07-17",
        "SOT: .claude/skills/weekly-devotion/devotion-data.json week 28",
        "",
        "---",
        "",
    ]
    image_lines = [
        "=== Week 28 매일묵상 이미지 프롬프트 ===",
        "생성일: 2026-07-07",
        "SOT: .claude/skills/weekly-devotion/devotion-data.json week 28",
        "공통 스타일 DNA: soft watercolor/gouache painting, hand-painted illustration, visible paper texture, muted earthy palette, generous negative space, contemplative, NOT photorealistic, NOT glossy AI illustration, no gradients",
        "",
    ]

    for entry in DAYS:
        common = {
            "제목": entry["adult_title"],
            "월": "7",
            "일": entry["day_num"],
            "요일": entry["weekday"],
            "성경_본문_전체": entry["adult_scripture"],
            "성경_구절_위치": entry["scripture_ref"],
            "해설_본문_각_문장_줄바꿈": "\n".join(entry["adult_reflection"]),
            "인용문": entry["adult_quote"],
            "인용_출처": "본문 묵상",
            "질문1_본문이해": entry["adult_questions"][0],
            "질문2_내면성찰": entry["adult_questions"][1],
            "질문3_실천적용": entry["adult_questions"][2],
            "기도문_각_문장_줄바꿈": sentence_lines(entry["adult_prayer"]),
            "추가_해시태그": entry["adult_tags"],
            "해설_단락들_p태그포함": p_tags(entry["adult_reflection"]),
            "기도문": entry["adult_prayer"],
        }
        youth = {
            "제목": entry["youth_title"],
            "월": "7",
            "일": entry["day_num"],
            "요일": entry["weekday"],
            "성경_구절_위치": entry["scripture_ref"],
            "성경_본문_전체_쉬운성경": entry["youth_scripture"],
            "묵상_단락들_p태그포함_strong볼드_포함": p_tags(entry["youth_reflection"]),
            "핵심_메시지_강조_인용": entry["youth_quote"],
            "질문1": entry["youth_questions"][0],
            "질문2": entry["youth_questions"][1],
            "질문3": entry["youth_questions"][2],
            "기도문_청소년_말투": entry["youth_prayer"],
            "해시태그": entry["youth_tags"],
        }

        (HTML_OUT / f"{entry['slug']}-adult-wordpress.html").write_text(
            replace_many(adult_wordpress, common), encoding="utf-8"
        )
        (HTML_OUT / f"{entry['slug']}-adult-a4.html").write_text(
            replace_many(adult_a4, common), encoding="utf-8"
        )
        (HTML_OUT / f"{entry['slug']}-youth-a4.html").write_text(
            replace_many(youth_a4, youth), encoding="utf-8"
        )

        adult_msgs.extend(
            [
                f"## {entry['weekday']}요일 (7/{entry['day_num']}) | {entry['scripture_ref']}",
                "",
                *entry["adult_kakao"],
                "",
                "---",
                "",
            ]
        )
        youth_msgs.extend(
            [
                f"## {entry['weekday']}요일 (7/{entry['day_num']}) | {entry['scripture_ref']}",
                "",
                *entry["youth_kakao"],
                "",
                "---",
                "",
            ]
        )
        image_lines.extend(
            [
                "──────────────────────────────────────",
                f"[{entry['slug'].upper()}] {entry['scripture_ref']} · {entry['adult_title']}",
                f"Style reference: src/Image_style_refernence/{entry['style_ref']} · Theme: {entry['image_theme']}",
                "──────────────────────────────────────",
                "[Midjourney]",
                f"/imagine prompt: {entry['mj']}",
                "",
                "[GPT-image-2]",
                entry["gpt"],
                "",
            ]
        )

    (OUT / "kakao-messages.md").write_text("\n".join(adult_msgs).strip() + "\n", encoding="utf-8")
    (OUT / "kakao-messages-youth.md").write_text("\n".join(youth_msgs).strip() + "\n", encoding="utf-8")
    (OUT / "image-prompts.txt").write_text("\n".join(image_lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
