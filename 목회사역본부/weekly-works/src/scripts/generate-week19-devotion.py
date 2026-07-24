from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".claude/skills/weekly-devotion/templates"
OUT = ROOT / "output/5월/2주차/매일묵상"
HTML_OUT = OUT / "html-original"


DAYS = [
    {
        "slug": "mon",
        "weekday": "월",
        "day_num": "11",
        "scripture_ref": "디모데전서 5:1-2",
        "adult_title": "가족처럼 대하는 존중",
        "youth_title": "사람을 대하는 말투가 믿음을 보여줘",
        "adult_scripture": "늙은이를 꾸짖지 말고 권하되 아버지에게 하듯 하며 젊은이에게는 형제에게 하듯 하고 늙은 여자에게는 어머니에게 하듯 하며 젊은 여자에게는 일절 깨끗함으로 자매에게 하듯 하라",
        "youth_scripture": "나이 많은 남자는 아버지처럼, 젊은 남자는 형제처럼 대하십시오. 나이 많은 여자는 어머니처럼, 젊은 여자는 깨끗한 마음으로 자매처럼 대하십시오.",
        "adult_reflection": [
            "바울은 디모데에게 교회 공동체를 다루는 방법을 말하면서 먼저 태도의 질서를 세웁니다. 연장자는 아버지처럼, 젊은이는 형제처럼, 연장자는 어머니처럼, 젊은 여자는 자매처럼 대하라는 권면은 교회가 단순한 조직이 아니라 하나님 안에서 새롭게 맺어진 가족임을 보여 줍니다. 그러므로 공동체 안의 관계는 효율과 역할보다 인격적 존중이 먼저입니다.",
            "이 말씀은 단지 예의범절을 말하는 것이 아닙니다. 바울은 특히 '꾸짖지 말고 권하라'고 말합니다. 진리를 말해야 할 때조차 상대를 꺾거나 모욕하는 방식이 아니라, 살리고 세우는 마음으로 말하라는 뜻입니다. 옳은 말을 하더라도 사랑이 빠지면 공동체는 상처를 입습니다. 존중은 진리를 약하게 만드는 것이 아니라, 진리가 사람을 살리는 통로가 되게 합니다.",
            "예수님께서 우리를 대하신 방식도 이와 같습니다. 주님은 우리의 죄를 드러내시되 모욕하지 않으셨고, 회개를 부르시되 정죄로 밀어붙이지 않으셨습니다. 먼저 우리를 품으신 사랑이 있었기에 우리는 변화로 초대받았습니다. 오늘 우리의 말과 시선도 그 복음의 방식을 닮아야 합니다. 가까운 사람일수록 함부로 대하지 않고, 가족처럼 정결하고 따뜻하게 대하는 것이 존중의 시작입니다.",
        ],
        "adult_quote": "사랑은 상대를 이용할 대상이 아니라 하나님께서 맡기신 사람으로 바라보게 합니다.",
        "adult_quote_source": "존 스토트",
        "adult_questions": [
            "나는 가까운 사람일수록 더 거칠게 대하고 있지는 않습니까?",
            "오늘 내 말투와 표정 안에 가족처럼 여기는 존중이 담겨 있습니까?",
            "주님께서 맡기신 사람 한 명에게 더 따뜻하게 대하기 위해 무엇을 바꾸겠습니까?",
        ],
        "adult_prayer": "주님, 사람을 편의와 감정으로 대하던 제 마음을 돌아봅니다. 교회와 가정에서 만나는 이들을 가족처럼 존중하게 하시고, 제 말투와 시선 안에 주님의 따뜻함이 드러나게 하소서. 가까운 사람일수록 더 정결하고 진실하게 대하게 하옵소서.",
        "adult_tags": "#존중 #공동체 #디모데전서 #가족같은사랑 #월요일묵상",
        "youth_reflection": [
            "학교에서 누구를 대하는 말투를 보면 그 사람 마음이 거의 보여요. 바울은 믿음이 교회에서 하는 말보다 <strong>사람을 대하는 태도</strong>에서 드러난다고 말해요. 특히 나이, 친함, 힘의 차이 때문에 누군가를 막 대하지 말라고 하죠.",
            "바울은 사람을 '아버지, 어머니, 형제, 자매처럼' 대하라고 해요. 이 말은 교회 안에서만 예쁘게 행동하라는 뜻이 아니라, 하나님이 맡기신 사람을 가족처럼 소중히 여기라는 뜻이에요. 무심코 던진 농담, 짜증 섞인 대답, 사람을 낮춰 보는 눈빛 하나가 누군가에게 오래 남을 수 있어요.",
            "예수님은 우리를 부끄럽게 몰아붙이기보다 사랑으로 바로잡으셨어요. 그래서 우리도 누군가를 고칠 때 상처 주는 말보다 세워 주는 말을 배워야 해요. 오늘 예수님이 내 입술을 업데이트하신다고 생각해 보세요. 친구와 가족을 함부로 대하는 대신, 형제자매처럼 깨끗하고 따뜻하게 말하는 하루가 될 수 있어요.",
        ],
        "youth_quote": "핵심 메시지: 믿음은 사람을 대하는 말투에서 드러나!",
        "youth_questions": [
            "나는 친한 친구일수록 더 막 대하고 있지 않나요?",
            "오늘 내 말 때문에 힘들었을 사람은 없을까요?",
            "가족처럼 존중하며 말하기 위해 오늘 바꿀 한 문장은 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 기분 따라 사람을 대할 때가 많아요. 오늘은 누군가를 함부로 말하지 않게 해 주세요. 친구도, 선생님도, 가족도 소중한 사람으로 보고 따뜻하게 말하게 해 주세요.",
        "youth_tags": "#청소년QT #존중하는말 #월요일QT #사람을대하는태도 #디모데전서",
        "adult_kakao": [
            "📖 오늘의 묵상 | 5월 11일 월요일",
            "",
            "\"늙은이를 꾸짖지 말고 권하되 아버지에게 하듯 하며\"",
            "— 디모데전서 5:1",
            "",
            "새 한 주를 시작하며, 사람을 대하는 말투부터 돌아봅니다.",
            "가까운 사람일수록 더 존중하는 마음이 필요합니다.",
            "가족처럼 대하는 존중, 오늘의 묵상으로 함께 시작해요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 5월 11일 월요일",
            "",
            "\"젊은 여자는 깨끗한 마음으로 자매처럼 대하십시오\"",
            "— 디모데전서 5:2",
            "",
            "말투 하나가 내 마음을 보여줘.",
            "오늘은 사람을 함부로 대하지 말고, 형제자매처럼 소중히 대해 보자.",
            "월요일 QT로 입술부터 새롭게 시작!",
            "",
            "#청소년QT #월요일QT #존중하는말 #사람을소중히",
        ],
        "image_prompt": {
            "theme": "존중과 가족 같은 시선",
            "mj": "A gentle domestic illustration of several chairs gathered around a warmly lit table, one folded letter and a pair of reading glasses resting neatly, soft morning light, cream and olive palette, atmosphere of family-like respect and careful speech, minimal devotional mood, clean composition, vertical 4:5 format --ar 4:5 --v 7",
            "gpt": "Create a vertical 4:5 devotional illustration showing a warm family-like atmosphere through symbolic objects: a tidy wooden table, a folded letter, simple chairs, and soft morning light. Use a calm cream, olive, and muted brown palette. Convey respect, purity, and tenderness in how people are regarded, without showing a crowd. Quiet, uncluttered, reverent composition.",
        },
    },
    {
        "slug": "tue",
        "weekday": "화",
        "day_num": "12",
        "scripture_ref": "베드로전서 2:17",
        "adult_title": "모든 사람을 귀하게 여기라",
        "youth_title": "모두를 존중하는 사람이 진짜 강해",
        "adult_scripture": "뭇 사람을 공경하며 형제를 사랑하며 하나님을 두려워하며 왕을 존대하라",
        "youth_scripture": "모든 사람을 존중하고, 믿는 형제자매를 사랑하고, 하나님을 두려워하고, 왕을 존경하십시오.",
        "adult_reflection": [
            "베드로는 단 한 절 안에 성도의 관계 윤리를 압축해서 보여 줍니다. '모든 사람을 공경하라'는 명령이 먼저 나오고, 그다음 형제를 사랑하고, 하나님을 두려워하며, 왕을 존대하라고 말합니다. 이 순서는 중요합니다. 그리스도인의 존중은 상황 따라 달라지는 예절이 아니라 하나님을 경외하는 마음에서 모든 사람에게 흘러가는 태도입니다.",
            "우리는 본능적으로 나와 맞는 사람에게는 따뜻하고, 불편한 사람에게는 차갑습니다. 그러나 베드로는 존중의 범위를 좁히지 않습니다. '모든 사람'이라는 표현은 나와 가까운 사람, 나와 다른 사람, 심지어 나를 불편하게 하는 사람까지 포함합니다. 상대가 내 기준에 합당해서가 아니라 하나님의 형상대로 지음받은 존재이기 때문에 존중받아야 한다는 뜻입니다.",
            "형제를 사랑한다는 말과 하나님을 두려워한다는 말이 함께 놓인 것도 의미가 깊습니다. 하나님을 진지하게 경외하는 사람은 사람을 함부로 다룰 수 없습니다. 주님 앞에서 낮아진 마음은 타인을 가볍게 보지 않게 만듭니다. 오늘 우리의 존중이 선택적인 친절이 아니라 믿음의 열매가 되기를 바랍니다. 주님이 귀히 여기시는 사람을 나도 귀히 여길 때, 세상은 복음의 질서를 보게 됩니다.",
        ],
        "adult_quote": "하나님을 경외하는 사람은 사람을 함부로 대할 수 없습니다.",
        "adult_quote_source": "존 칼빈",
        "adult_questions": [
            "나는 어떤 사람을 마음속에서 쉽게 낮춰 보고 있습니까?",
            "모든 사람을 공경하라는 말씀이 오늘 내 관계를 어떻게 비추고 있습니까?",
            "하나님을 경외하는 마음으로 누군가를 귀하게 대할 구체적 행동은 무엇입니까?",
        ],
        "adult_prayer": "하나님, 사람을 제 기준으로 나누고 판단하던 마음을 내려놓습니다. 모든 사람을 공경하고 형제를 사랑하며 주님을 경외하는 균형 잡힌 마음을 주소서. 오늘 만나는 이들을 귀히 여기시는 주님의 눈을 제게도 허락하옵소서.",
        "adult_tags": "#공경 #형제사랑 #경외 #베드로전서 #화요일묵상",
        "youth_reflection": [
            "강한 척하는 건 쉽지만, 모두를 존중하는 건 진짜 힘이 필요해요. 베드로는 믿는 사람만이 아니라 <strong>모든 사람</strong>을 존중하라고 말해요. 내 편인 사람만 챙기는 건 자연스럽지만, 나와 다른 사람도 귀하게 보는 건 훈련이 필요하죠.",
            "성경은 형제를 사랑하라고 하면서 동시에 하나님을 두려워하라고 말해요. 이 둘이 연결돼 있다는 게 중요해요. 하나님을 진짜 크게 보는 사람은 다른 사람을 작게 보지 못해요. 반대로 사람을 함부로 대하면, 사실은 하나님을 가볍게 여긴다는 뜻일 수도 있어요.",
            "오늘 학교에서 '나랑 안 맞는 사람' 한 명을 떠올려 보세요. 무시하지 않고, 대충 넘기지 않고, 한마디라도 존중으로 반응하는 선택을 해 보세요. 그런 작은 태도가 믿음을 꽤 크게 보여줄 수 있어요. 성숙함은 센 척하는 데 있지 않고, 모두를 귀히 여기는 데 있어요.",
        ],
        "youth_quote": "핵심 메시지: 모두를 존중하는 사람이 진짜 멋있다!",
        "youth_questions": [
            "나는 어떤 사람을 무시하거나 피하고 싶어 하나요?",
            "하나님을 경외한다는 게 친구 관계에선 어떻게 보일까요?",
            "오늘 존중을 보여줄 작은 행동 하나는 무엇인가요?",
        ],
        "youth_prayer": "하나님, 저도 모르게 사람을 등급 매기듯 볼 때가 있어요. 오늘은 누구도 무시하지 않게 해 주세요. 나와 다른 사람도 존중하고, 친구들을 사랑으로 대하는 용기를 주세요.",
        "youth_tags": "#청소년QT #모두를존중 #화요일QT #형제사랑 #베드로전서",
        "adult_kakao": [
            "📖 오늘의 묵상 | 5월 12일 화요일",
            "",
            "\"뭇 사람을 공경하며 형제를 사랑하며\"",
            "— 베드로전서 2:17",
            "",
            "존중은 일부 사람에게만 보이는 친절이 아닙니다.",
            "하나님을 경외하는 마음은 모든 사람을 귀하게 보게 합니다.",
            "오늘 한 사람을 더 귀히 여기는 화요일 묵상입니다.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 5월 12일 화요일",
            "",
            "\"모든 사람을 존중하십시오\"",
            "— 베드로전서 2:17",
            "",
            "나랑 친한 사람만 챙기는 건 쉽지.",
            "근데 모두를 존중하는 건 진짜 믿음의 힘이야.",
            "오늘 무시 대신 존중을 선택해 보자!",
            "",
            "#청소년QT #화요일QT #모두를존중 #진짜성숙",
        ],
        "image_prompt": {
            "theme": "모든 사람을 귀하게 여기는 시선",
            "mj": "An elegant scene of different pairs of shoes neatly lined at a doorway, soft natural light falling evenly on each pair, symbolic of honoring every person equally, calm cream and sage palette, minimal devotional illustration, clean negative space, vertical 4:5 format --ar 4:5 --v 7",
            "gpt": "Create a vertical 4:5 devotional illustration showing several different pairs of shoes arranged neatly at a doorway, each receiving the same soft light. Use this as a symbol of honoring every person equally before God. Keep the palette warm cream, sage green, and muted earth tones. Quiet, minimal, reverent, uncluttered composition.",
        },
    },
    {
        "slug": "wed",
        "weekday": "수",
        "day_num": "13",
        "scripture_ref": "로마서 12:10",
        "adult_title": "먼저 존경하는 사랑",
        "youth_title": "먼저 챙겨주는 게 사랑이야",
        "adult_scripture": "형제를 사랑하여 서로 우애하고 존경하기를 서로 먼저 하며",
        "youth_scripture": "형제자매처럼 서로 사랑하고, 서로 먼저 존중해 주십시오.",
        "adult_reflection": [
            "로마서 12장에서 바울은 공동체의 사랑이 추상적인 감정으로 끝나지 않도록 구체적인 방향을 제시합니다. 형제를 사랑하고 서로 우애하라는 말 뒤에 '존경하기를 서로 먼저 하라'는 명령을 붙이는 것은 매우 인상적입니다. 사랑은 마음속 호감으로 머물지 않고, 상대를 높여 주는 태도로 드러나야 하기 때문입니다.",
            "우리는 존중받고 싶은 마음이 강합니다. 그래서 누가 먼저 인사하는지, 누가 먼저 알아주는지, 누가 먼저 사과하는지를 따지며 쉽게 마음을 닫습니다. 그러나 복음은 계산하는 관계를 깨뜨립니다. 예수님은 우리가 먼저 사랑받을 자격을 보이기 전에 먼저 다가오셨고, 먼저 자신을 낮추셨습니다. 그 사랑을 아는 사람은 존중을 미루지 않고 먼저 건넵니다.",
            "오늘 우리의 가정과 공동체에 필요한 것은 더 화려한 말이나 더 많은 지식이 아니라 먼저 움직이는 사랑입니다. 상대를 끝까지 들으려는 경청, 먼저 인사하는 태도, 다른 사람을 세워 주는 언어는 공동체의 질서를 회복합니다. 존경하기를 먼저 하는 사람을 통해 주님은 관계 안에 새로운 공기를 불어넣으십니다.",
        ],
        "adult_quote": "겸손은 자신을 작게 만드는 것이 아니라, 타인을 먼저 보게 만드는 은혜입니다.",
        "adult_quote_source": "팀 켈러",
        "adult_questions": [
            "나는 존중받고 싶은 마음 때문에 먼저 사랑하지 못하고 있지는 않습니까?",
            "오늘 내가 먼저 세워 주어야 할 사람은 누구입니까?",
            "존경하기를 먼저 한다는 말씀이 내 말과 행동에 어떤 변화를 요구합니까?",
        ],
        "adult_prayer": "주님, 인정받고 싶은 마음이 커서 먼저 사랑하고 먼저 존중하기를 미루었던 저를 용서하소서. 예수님께서 먼저 다가오신 사랑을 기억하며 오늘 제가 먼저 인사하고 먼저 경청하고 먼저 세워 주게 하옵소서.",
        "adult_tags": "#우애 #먼저존경 #로마서 #공동체사랑 #수요일묵상",
        "youth_reflection": [
            "누가 먼저 사과할까, 누가 먼저 말 걸까, 누가 먼저 챙길까. 우리는 보통 기다리죠. 자존심이 상할까 봐, 괜히 내가 손해 보는 것 같아서 먼저 움직이기 싫을 때가 많아요. 그런데 바울은 <strong>먼저 존중하라</strong>고 말해요.",
            "먼저 챙겨주는 건 자존심이 약해서가 아니라 사랑이 강해서예요. 예수님도 우리를 기다리게 하지 않으시고 먼저 다가오셨어요. 그래서 믿음은 '나도 무시당하기 싫어'라는 마음보다 '내가 먼저 사랑해 볼게'라는 용기로 보이기 시작해요.",
            "오늘 먼저 인사하고, 먼저 들어주고, 먼저 칭찬해 보세요. 별거 아닌 것 같아도 관계의 분위기는 진짜 달라질 수 있어요. 먼저 존중하는 사람은 공동체 안에 평화를 가져오는 사람이에요. 그 작은 시작이 예수님을 닮아 가는 훈련이 됩니다.",
        ],
        "youth_quote": "핵심 메시지: 먼저 챙겨주는 사람이 사랑을 시작한다!",
        "youth_questions": [
            "나는 보통 누가 먼저 다가오길 기다리나요?",
            "먼저 존중한다는 건 학교에서 어떤 행동으로 보일까요?",
            "오늘 내가 먼저 해볼 수 있는 친절 한 가지는 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 자존심 때문에 먼저 다가가기 싫을 때가 많아요. 오늘은 먼저 인사하고 먼저 챙겨주는 용기를 주세요. 제 작은 친절로 누군가의 마음이 따뜻해지게 해 주세요.",
        "youth_tags": "#청소년QT #먼저존중 #수요일QT #먼저다가가기 #로마서",
        "adult_kakao": [
            "📖 오늘의 묵상 | 5월 13일 수요일",
            "",
            "\"존경하기를 서로 먼저 하며\"",
            "— 로마서 12:10",
            "",
            "사랑은 기다리는 마음보다 먼저 움직이는 태도에 가깝습니다.",
            "오늘 먼저 건네는 인사와 경청이 공동체를 따뜻하게 할 수 있습니다.",
            "수요일 묵상으로 ‘먼저 존중하는 사랑’을 연습해 보세요.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 5월 13일 수요일",
            "",
            "\"서로 먼저 존중해 주십시오\"",
            "— 로마서 12:10",
            "",
            "먼저 다가가는 건 지는 게 아니야.",
            "오히려 사랑을 시작하는 진짜 용기지.",
            "오늘 먼저 인사하고 먼저 칭찬해 보자!",
            "",
            "#청소년QT #수요일QT #먼저존중 #용기있는친절",
        ],
        "image_prompt": {
            "theme": "먼저 다가가는 존중",
            "mj": "Two simple hands offering a small stool for another to sit, warm afternoon light, humble and tender gesture, symbolic of honoring another first, soft olive and cream palette, minimal devotional illustration, vertical 4:5 format --ar 4:5 --v 7",
            "gpt": "Create a vertical 4:5 devotional illustration of a humble gesture: one person quietly offering a stool or chair for another first. Keep the scene symbolic and minimal, with warm afternoon light and a soft olive, cream, and muted brown palette. Convey honoring another before oneself. Reverent, uncluttered, gentle composition.",
        },
    },
    {
        "slug": "thu",
        "weekday": "목",
        "day_num": "14",
        "scripture_ref": "고린도전서 13:4-7",
        "adult_title": "사랑은 태도로 증명됩니다",
        "youth_title": "사랑은 감정보다 행동이야",
        "adult_scripture": "사랑은 오래 참고 사랑은 온유하며 시기하지 아니하며 사랑은 자랑하지 아니하며 교만하지 아니하며 무례히 행하지 아니하며 자기의 유익을 구하지 아니하며 성내지 아니하며 악한 것을 생각하지 아니하며 불의를 기뻐하지 아니하며 진리와 함께 기뻐하고 모든 것을 참으며 모든 것을 믿으며 모든 것을 바라며 모든 것을 견디느니라",
        "youth_scripture": "사랑은 오래 참고 친절합니다. 사랑은 교만하지 않고 무례하지 않습니다. 자기 유익만 구하지 않고 쉽게 화내지 않습니다. 사랑은 모든 것을 참고 믿고 바라고 견딥니다.",
        "adult_reflection": [
            "고린도전서 13장은 사랑이 무엇을 느끼는가보다 사랑이 어떻게 행동하는가를 보여 줍니다. 오래 참고, 온유하고, 교만하지 않으며, 무례히 행하지 않고, 자기 유익을 구하지 않는다는 설명은 사랑이 단순한 감정이 아니라 삶의 태도라는 사실을 드러냅니다. 바울은 사랑을 추상적으로 찬양하지 않고, 공동체 속에서 실제로 드러나야 할 성품으로 묘사합니다.",
            "이 말씀 앞에 서면 우리는 쉽게 자신의 빈자리를 보게 됩니다. 사랑한다고 말하면서도 쉽게 조급해지고, 상처받으면 오래 기억하고, 내 입장과 내 유익을 먼저 챙기기 때문입니다. 그래서 사랑장은 우리를 정죄하기 위한 기준표가 아니라, 우리 안에 사랑이 얼마나 필요한지를 보여 주는 거울이 됩니다. 참사랑은 인간의 의지로 짜내는 성품이 아니라 그리스도의 사랑이 우리 안에서 빚어 가는 열매입니다.",
            "예수님은 우리에게 오래 참으셨고, 무례히 대하지 않으셨고, 끝까지 견디셨습니다. 그 복음 안에 머무를 때 비로소 우리도 사랑을 행동으로 배워 갑니다. 오늘 하나님은 사랑을 크게 느끼고 있는지보다 사랑답게 반응하고 있는지를 물으십니다. 오래 참는 한마디, 온유한 표정, 내 유익을 내려놓는 선택 안에 복음의 능력이 드러납니다.",
        ],
        "adult_quote": "사랑은 위대한 감정보다 작은 순종 속에서 더 자주 드러납니다.",
        "adult_quote_source": "존 파이퍼",
        "adult_questions": [
            "고린도전서 13장의 사랑 중 지금 내게 가장 부족한 모습은 무엇입니까?",
            "나는 사랑을 감정으로만 생각하고 있지는 않습니까?",
            "오늘 오래 참고 온유하게 반응해야 할 상황은 어디에 있습니까?",
        ],
        "adult_prayer": "사랑의 주님, 제 감정이 앞서서 쉽게 무례해지고 조급해지는 저를 불쌍히 여겨 주소서. 오래 참고 온유하신 예수님의 사랑이 제 마음을 다스리게 하시고, 오늘 제 작은 태도 속에 사랑의 열매가 맺히게 하옵소서.",
        "adult_tags": "#사랑장 #오래참음 #온유 #고린도전서 #목요일묵상",
        "youth_reflection": [
            "사랑하면 다 괜찮아질 것 같지만, 성경은 사랑을 감정보다 <strong>행동</strong>으로 설명해요. 오래 참고, 친절하고, 무례하지 않고, 자기 유익만 구하지 않는 것. 이게 사랑의 진짜 모양이에요. 그러니까 사랑은 '좋아해'라고 말하는 것보다 훨씬 깊은 거예요.",
            "좋아한다고 말하면서 짜증 내고, 챙긴다면서 내 기분만 앞세우면 그건 사랑이 아니겠죠. 바울은 사랑을 태도로 설명해요. 내가 기분 좋을 때만 친절한 건 쉬워요. 그런데 힘들 때도 오래 참고, 화날 때도 무례하지 않은 건 예수님을 닮아 가는 훈련이에요.",
            "예수님은 우리를 향해 오래 참아 주시고 끝까지 견디셨어요. 그래서 우리도 배울 수 있어요. 오늘 누군가를 사랑한다면 말보다 태도로 보여 주세요. 참는 것, 친절하게 말하는 것, 내 기분보다 상대를 생각하는 것부터 시작해 봐요. 작은 태도가 사랑의 진심을 드러냅니다.",
        ],
        "youth_quote": "핵심 메시지: 사랑은 느낌보다 태도로 보인다!",
        "youth_questions": [
            "나는 사랑을 말로만 하고 행동은 다르게 할 때가 없나요?",
            "오늘 ‘오래 참음’이 필요한 사람은 누구인가요?",
            "친절한 태도로 사랑을 보여줄 한 가지 행동은 무엇인가요?",
        ],
        "youth_prayer": "예수님, 저는 기분 좋을 때만 사랑하려고 할 때가 많아요. 오늘은 제 감정보다 사랑의 태도를 선택하게 해 주세요. 오래 참고 친절하게 말하고, 무례하지 않게 행동하게 해 주세요.",
        "youth_tags": "#청소년QT #사랑은행동 #목요일QT #친절과참음 #고린도전서",
        "adult_kakao": [
            "📖 오늘의 묵상 | 5월 14일 목요일",
            "",
            "\"사랑은 오래 참고 사랑은 온유하며\"",
            "— 고린도전서 13:4",
            "",
            "사랑은 감정보다 태도에서 더 또렷하게 드러납니다.",
            "오늘 오래 참고 온유하게 반응하는 작은 순종이 복음의 향기가 됩니다.",
            "목요일 묵상에서 사랑의 실제 모습을 다시 배웁니다.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 5월 14일 목요일",
            "",
            "\"사랑은 오래 참고 친절합니다\"",
            "— 고린도전서 13:4",
            "",
            "사랑은 말보다 태도야.",
            "오늘 짜증 대신 친절, 급함 대신 참음을 선택해 보자.",
            "그게 진짜 사랑의 시작이야!",
            "",
            "#청소년QT #목요일QT #사랑은행동 #친절선택",
        ],
        "image_prompt": {
            "theme": "태도로 드러나는 사랑",
            "mj": "A pair of hands carefully mending torn fabric with patient stitches, soft evening light, symbolic of love that endures and restores, gentle cream, sage, and warm thread colors, devotional minimal illustration, vertical 4:5 format --ar 4:5 --v 7",
            "gpt": "Create a vertical 4:5 devotional illustration of patient hands mending torn fabric with careful stitches. Use this as a symbol of love that endures, restores, and does not act rudely. Keep the palette soft cream, sage green, and warm thread colors. Quiet evening light, minimal, reverent, uncluttered composition.",
        },
    },
    {
        "slug": "fri",
        "weekday": "금",
        "day_num": "15",
        "scripture_ref": "빌립보서 2:3-4",
        "adult_title": "자기보다 남을 낫게 여기는 마음",
        "youth_title": "내 중심에서 우리 중심으로",
        "adult_scripture": "아무 일에든지 다툼이나 허영으로 하지 말고 오직 겸손한 마음으로 각각 자기보다 남을 낫게 여기고 각각 자기 일을 돌볼뿐더러 또한 각각 다른 사람들의 일을 돌보아 나의 기쁨을 충만하게 하라",
        "youth_scripture": "이기적인 마음이나 자랑하려는 마음으로 하지 말고, 겸손하게 다른 사람을 자기보다 더 낫게 여기십시오. 자기 일만 보지 말고 다른 사람의 일도 돌아보십시오.",
        "adult_reflection": [
            "바울은 빌립보 교회에 권면하면서 공동체를 무너뜨리는 뿌리를 분명하게 짚습니다. 다툼과 허영은 결국 자기중심성에서 자랍니다. 내 의견, 내 감정, 내 유익이 중심이 될수록 공동체는 메말라 가고, 다른 사람을 세우는 시선은 약해집니다. 그래서 바울은 겸손한 마음으로 남을 자기보다 낫게 여기라고 권합니다.",
            "겸손은 자신을 쓸모없게 여기는 열등감이 아닙니다. 오히려 자기 자신에게만 몰려 있던 시선이 다른 사람에게로 옮겨 가는 영적 전환입니다. 예수님은 하나님과 동등되심을 취할 것으로 여기지 않으시고 자신을 비워 종의 형체를 입으셨습니다. 그 복음을 아는 사람은 자기 일만 붙드는 삶에서 벗어나, 다른 사람의 필요와 아픔을 실제로 돌아보게 됩니다.",
            "한 주의 끝에서 하나님은 우리의 시야를 넓혀 주십니다. 내 계획과 내 기분에만 갇혀 있는 삶은 결국 메말라 가지만, 옆 사람의 필요를 살피는 삶은 공동체를 살리고 우리 영혼도 넓어지게 합니다. 오늘 다른 사람의 일을 돌아보라는 바울의 권면은 부담스러운 추가 과제가 아니라, 그리스도를 닮아 가는 복된 초대입니다.",
        ],
        "adult_quote": "겸손은 자신을 덜 생각하는 것이 아니라 자신만 생각하지 않는 것입니다.",
        "adult_quote_source": "C.S. 루이스",
        "adult_questions": [
            "최근 나는 어떤 일에서 자기중심적인 태도를 보였습니까?",
            "다른 사람의 필요를 돌아보는 시선이 내 삶에서 얼마나 자주 작동하고 있습니까?",
            "오늘 내가 실제로 돌아볼 한 사람의 필요는 무엇입니까?",
        ],
        "adult_prayer": "주님, 제 안의 다툼과 허영을 내려놓게 하시고 겸손한 마음을 주소서. 저 자신만 돌보는 좁은 시선에서 벗어나 다른 이의 아픔과 필요를 살피게 하시며, 예수님의 낮아지심을 닮아 공동체를 세우는 사람이 되게 하옵소서.",
        "adult_tags": "#겸손 #타인돌봄 #빌립보서 #공동체세움 #금요일묵상",
        "youth_reflection": [
            "요즘은 '나'를 챙기는 게 너무 당연한 시대 같아요. 내 기분, 내 일정, 내 성적, 내 피드가 제일 중요해 보이죠. 그런데 바울은 내 일만 보지 말고 <strong>다른 사람의 일도 돌아보라</strong>고 말해요. 그건 남을 위해 나를 완전히 없애라는 뜻이 아니라, 시선을 넓히라는 초대예요.",
            "겸손은 주눅 드는 게 아니라 시야가 넓어지는 거예요. 내 문제만 크게 보이던 눈이 옆 친구의 마음도 보게 되는 거죠. 예수님은 늘 그렇게 사셨어요. 사람들의 필요를 그냥 지나치지 않으셨고, 자기보다 남을 먼저 살피셨어요. 그래서 겸손은 약함이 아니라 예수님을 닮은 강함이에요.",
            "금요일엔 한 주를 마무리하면서 주변을 한번 둘러봐요. 도움이 필요한 친구, 지친 가족, 외로운 누군가를 그냥 지나치지 않는 마음이 진짜 겸손이에요. 오늘 다른 사람의 일을 돌아보는 작은 행동 하나가 누군가에겐 큰 위로가 될 수 있어요. 내 중심에서 우리 중심으로 옮겨 가는 것이 복음의 길입니다.",
        ],
        "youth_quote": "핵심 메시지: 내 일만 보지 말고 옆 사람도 살펴봐!",
        "youth_questions": [
            "나는 보통 내 문제와 내 감정에만 갇혀 있지 않나요?",
            "이번 주 내가 놓치고 있던 사람의 필요는 무엇일까요?",
            "오늘 다른 사람을 돌아보는 구체적인 행동 하나는 무엇인가요?",
        ],
        "youth_prayer": "예수님, 제 생각과 제 문제만 크게 보일 때가 많아요. 오늘은 제 시선을 넓혀 주세요. 친구와 가족의 필요를 살피고, 도울 수 있는 마음과 용기를 주세요.",
        "youth_tags": "#청소년QT #겸손 #금요일QT #다른사람돌아보기 #빌립보서",
        "adult_kakao": [
            "📖 오늘의 묵상 | 5월 15일 금요일",
            "",
            "\"각각 자기보다 남을 낫게 여기고\"",
            "— 빌립보서 2:3",
            "",
            "한 주의 끝에서 우리의 시선이 어디를 향하는지 돌아봅니다.",
            "내 일만 붙드는 마음에서 벗어나 다른 사람의 필요를 살피는 것이 겸손입니다.",
            "금요일 묵상으로 우리 중심의 삶을 배워 봅니다.",
            "",
            "#디딤교회 #매일묵상 #은혜누림",
        ],
        "youth_kakao": [
            "📖 오늘의 QT | 5월 15일 금요일",
            "",
            "\"자기 일만 보지 말고 다른 사람의 일도 돌아보십시오\"",
            "— 빌립보서 2:4",
            "",
            "이번 주 내 이야기만 너무 크게 보이지 않았어?",
            "오늘은 옆 사람 마음도 한번 살펴보자.",
            "그게 예수님 닮은 겸손이야!",
            "",
            "#청소년QT #금요일QT #겸손 #옆사람돌아보기",
        ],
        "image_prompt": {
            "theme": "내 중심에서 우리 중심으로",
            "mj": "A simple scene of one umbrella tilted to cover another person first in gentle rain, quiet compassionate gesture, muted blue-gray and warm olive palette, symbolic of caring for another's need before your own, minimal devotional illustration, vertical 4:5 format --ar 4:5 --v 7",
            "gpt": "Create a vertical 4:5 devotional illustration of a quiet compassionate moment: one umbrella being tilted to cover another person first in light rain. Use muted blue-gray, warm olive, and cream tones. Convey humility, care, and noticing another person's need before your own. Minimal, symbolic, reverent composition.",
        },
    },
]


def load_template(name: str) -> str:
    return (TEMPLATES / name).read_text(encoding="utf-8")


def replace_many(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace("{" + key + "}", value)
    return text


def p_tags(paragraphs: list[str]) -> str:
    return "\n".join(f"<p>{p}</p>" for p in paragraphs)


def lines(text: str) -> str:
    return "\n".join(text.split(". "))


def render():
    aw = load_template("adult-wordpress.html")
    aa = load_template("adult-a4.html")
    ya = load_template("youth-a4.html")

    adult_msgs = ["# 19주차 매일묵상 카카오톡 동기부여 메시지 (장년용)", "생성일: 2026-05-04", "", "테마: 존중 (딤전 5 / 벧전 2 / 롬 12 / 고전 13 / 빌 2)", "", "---", ""]
    youth_msgs = ["# 19주차 매일묵상 카카오톡 동기부여 메시지 (청소년용)", "생성일: 2026-05-04", "", "테마: 존중 (딤전 5 / 벧전 2 / 롬 12 / 고전 13 / 빌 2)", "", "---", ""]
    image_lines = [
        "=== Week 19 매일묵상 이미지 프롬프트 ===",
        "생성일: 2026-05-04",
        "테마: 존중 (Respect) — 딤전 5 / 벧전 2 / 롬 12 / 고전 13 / 빌 2",
        "공통 파라미터: --ar 4:5",
        "",
    ]

    for entry in DAYS:
        common = {
            "제목": entry["adult_title"],
            "월": "5",
            "일": entry["day_num"],
            "요일": entry["weekday"],
            "성경_본문_전체": entry["adult_scripture"],
            "성경_구절_위치": entry["scripture_ref"],
            "해설_본문_각_문장_줄바꿈": "\n".join(entry["adult_reflection"]),
            "인용문": entry["adult_quote"],
            "인용_출처": entry["adult_quote_source"],
            "질문1_본문이해": entry["adult_questions"][0],
            "질문2_내면성찰": entry["adult_questions"][1],
            "질문3_실천적용": entry["adult_questions"][2],
            "기도문_각_문장_줄바꿈": lines(entry["adult_prayer"]),
            "추가_해시태그": entry["adult_tags"],
            "해설_단락들_p태그포함": p_tags(entry["adult_reflection"]),
            "기도문": entry["adult_prayer"],
        }
        youth = {
            "제목": entry["youth_title"],
            "월": "5",
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

        (HTML_OUT / f"{entry['slug']}-adult-wordpress.html").write_text(replace_many(aw, common), encoding="utf-8")
        (HTML_OUT / f"{entry['slug']}-adult-a4.html").write_text(replace_many(aa, common), encoding="utf-8")
        (HTML_OUT / f"{entry['slug']}-youth-a4.html").write_text(replace_many(ya, youth), encoding="utf-8")

        adult_msgs.extend(
            [
                f"## {entry['weekday']}요일 (5/{entry['day_num']}) | {entry['scripture_ref']}",
                "",
                *entry["adult_kakao"],
                "",
                "---",
                "",
            ]
        )
        youth_msgs.extend(
            [
                f"## {entry['weekday']}요일 (5/{entry['day_num']}) | {entry['scripture_ref']}",
                "",
                *entry["youth_kakao"],
                "",
                "---",
                "",
            ]
        )
        image_lines.extend(
            [
                f"[{entry['slug'].upper()}] {entry['scripture_ref']} · {entry['image_prompt']['theme']}",
                "[Midjourney]",
                entry["image_prompt"]["mj"],
                "",
                "[GPT-image-2]",
                entry["image_prompt"]["gpt"],
                "",
                "──────────────────────────────────────",
                "",
            ]
        )

    (OUT / "kakao-messages-adult.md").write_text("\n".join(adult_msgs).strip() + "\n", encoding="utf-8")
    (OUT / "kakao-messages-youth.md").write_text("\n".join(youth_msgs).strip() + "\n", encoding="utf-8")
    (OUT / "image-prompts.txt").write_text("\n".join(image_lines).strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    render()
