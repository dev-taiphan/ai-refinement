# Hướng dẫn cài đặt và sử dụng plugin kaiz (software factory)

Plugin này biến các GitHub issue thành pull request. Bạn gắn label `factory`
cho issue, chạy một lệnh, và một nhóm agent Claude sẽ lần lượt đánh giá issue,
viết đặc tả, viết code, chạy kiểm thử, review và quyết định merge. Việc gì
agent không chắc chắn thì được chuyển lại cho bạn.

Mục lục:

1. [Cách factory hoạt động](#1-cách-factory-hoạt-động)
2. [Chuẩn bị máy](#2-chuẩn-bị-máy)
3. [Cài plugin](#3-cài-plugin)
4. [Cài factory vào một repo](#4-cài-factory-vào-một-repo)
5. [Sử dụng hằng ngày](#5-sử-dụng-hằng-ngày)
6. [Xử lý job cần con người](#6-xử-lý-job-cần-con-người)
7. [Dashboard](#7-dashboard)
8. [Cấu hình](#8-cấu-hình)
9. [Chi phí và an toàn](#9-chi-phí-và-an-toàn)
10. [Cập nhật và gỡ cài đặt](#10-cập-nhật-và-gỡ-cài-đặt)
11. [Xử lý sự cố](#11-xử-lý-sự-cố)
12. [Phân tích ticket cục bộ (không cần GitHub)](#12-phân-tích-ticket-cục-bộ-không-cần-github)

---

## 1. Cách factory hoạt động

Mỗi issue có label `factory` trở thành một **job**. Job đi qua các bước sau:

| Bước | Ai làm | Kết quả |
|---|---|---|
| intake | agent `intake` (Fable) | ACCEPT, NEEDS-INFO (hỏi lại tác giả) hoặc REJECT |
| route | script `factory/bin/route` | chọn reviewer và model theo mức rủi ro |
| spec | agent `spec-writer` (Opus) | `spec.md` với tiêu chí nghiệm thu kiểm thử được |
| build | agent `builder` (Opus) | commit, push nhánh `factory/<job-id>`, mở PR nháp |
| gate | script `factory/bin/gate` | chạy `factory/checks.sh`; FAIL thì quay lại build |
| review | các agent reviewer | code luôn có; thêm UX/UI khi đổi giao diện, security khi có rủi ro bảo mật |
| approve | agent `approver` (Opus) | APPROVE thì merge PR; ESCALATE thì gắn label `factory:needs-human` |

Một job có tối đa `max_rounds` vòng (mặc định 3). Mỗi vòng gồm build, gate và
review. Hết số vòng mà chưa qua thì job chuyển sang chờ con người.

Mỗi job làm việc trong một git worktree riêng tại `.worktrees/<job-id>`, nên
nhiều job chạy song song không đụng nhau, và thư mục làm việc chính của bạn
không bị thay đổi. Trạng thái job nằm trong `factory/jobs/`, nên nếu phiên
Claude bị tắt giữa chừng, lần chạy sau sẽ tiếp tục từ chỗ đã dừng.

---

## 2. Chuẩn bị máy

Cần có:

| Công cụ | Phiên bản | Kiểm tra |
|---|---|---|
| Claude Code | 2.1.257 trở lên | `claude --version` |
| Git (kèm Git Bash trên Windows) | bất kỳ | `git --version` |
| Python | 3.10 trở lên, gọi được bằng lệnh `python3` | `python3 --version` |
| GitHub CLI | bất kỳ, đã đăng nhập | `gh auth status` |

Tài khoản GitHub đăng nhập trong `gh` phải có quyền push vào repo và quản lý
label.

### Trên Windows

**GitHub CLI:**

```powershell
winget install --id GitHub.cli
gh auth login
```

Mở terminal mới sau khi cài để PATH được cập nhật.

**Lệnh `python3`.** Python cài từ python.org chỉ có `python.exe`, còn
`python3` trên Windows thường trỏ tới alias của Microsoft Store, không chạy
được script. Các script của factory gọi `python3`, nên cần hai bước:

1. Tắt alias: Settings → Apps → Advanced app settings → App execution aliases,
   tắt cả hai mục `python.exe` và `python3.exe` (App Installer).
2. Tạo `python3.exe` bên cạnh `python.exe` (đổi `Python314` cho đúng phiên bản
   đã cài):

   ```powershell
   $py = "$env:LOCALAPPDATA\Programs\Python\Python314"
   Copy-Item "$py\python.exe" "$py\python3.exe"
   ```

Mở terminal mới và chạy `python3 --version`. Lệnh phải in ra phiên bản Python,
không mở Microsoft Store.

**Git Bash.** Các script và `checks.sh` chạy bằng bash. Git for Windows đã kèm
sẵn Git Bash, và Claude Code trên Windows dùng nó để chạy lệnh.

### Trên macOS / Linux

```bash
brew install gh        # hoặc theo hướng dẫn tại https://cli.github.com
gh auth login
python3 --version      # thường đã có sẵn
```

---

## 3. Cài plugin

Plugin chạy được trong Claude Code ở terminal (TUI), trong extension VS Code và
trong các phiên **local** của ứng dụng Claude Desktop (tab Code). Plugin không
chạy trong phiên cloud, phiên WSL hay ứng dụng chat claude.ai, vì factory cần
git, `gh` và Python trên máy của bạn.

Repo này là một marketplace tên `ai-factory` với **hai plugin**:

| Plugin | Lệnh | Nội dung | Cần gì |
|---|---|---|---|
| `kaiz` | `/kaiz:analyze` | phân tích ticket cục bộ (mục 12); chỉ có Markdown, không có script | chỉ Claude Code |
| `kaiz-factory` | `/kaiz-factory:init`, `/kaiz-factory:factory` | pipeline GitHub issue → PR (mục 1 đến 11) | `gh`, Python, Git Bash |

Chỉ dùng phân tích ticket thì cài `kaiz` là đủ, không cần mục 2.

### Cách A: từ thư mục trên máy

Gõ trong Claude Code:

```
/plugin marketplace add d:/ai-factory-plugin
/plugin install kaiz@ai-factory
/plugin install kaiz-factory@ai-factory
```

### Cách B: từ GitHub (để chia sẻ cho người khác)

Đẩy thư mục `ai-factory-plugin` lên một repo GitHub, ví dụ
`your-org/ai-factory-plugin`. Người dùng gõ:

```
/plugin marketplace add your-org/ai-factory-plugin
/plugin install kaiz@ai-factory
/plugin install kaiz-factory@ai-factory
```

Nếu repo là private, người cài phải có quyền đọc repo đó.

Cũng có thể cài từ shell thay vì trong phiên Claude:

```bash
claude plugin marketplace add your-org/ai-factory-plugin
claude plugin install kaiz@ai-factory
claude plugin install kaiz-factory@ai-factory
```

### Chọn phạm vi cài

Khi chạy `/plugin install`, Claude Code hỏi phạm vi:

- **User:** dùng cho mọi project trên máy, và dùng chung giữa terminal, VS Code
  và Desktop. Phù hợp khi bạn dùng factory cho nhiều repo.
- **Project:** ghi vào `.claude/settings.json` của repo, nên cả nhóm cùng được
  nhắc cài khi mở repo đó.

### Kiểm tra

Gõ `/plugin` và xem `kaiz` và `kaiz-factory` có trong danh sách đã cài. Gõ `/` sẽ
thấy các lệnh của chúng: `/kaiz:analyze`, `/kaiz-factory:init` và
`/kaiz-factory:factory`.

### Dùng thử không cài

```bash
claude --plugin-dir d:/ai-factory-plugin
```

Plugin chỉ có hiệu lực trong phiên đó.

---

## 4. Cài factory vào một repo

Plugin cung cấp agent và lệnh. Mỗi repo cần thêm thư mục `factory/` riêng chứa
script, cấu hình và lệnh kiểm thử của repo đó. Làm việc này **một lần cho mỗi
repo**.

1. Mở Claude Code ở thư mục gốc của repo. Repo phải có remote `origin` trên
   GitHub.
2. Chạy:

   ```
   /kaiz-factory:init
   ```

Claude sẽ:

- kiểm tra các yêu cầu ở mục 2 và dừng lại báo lỗi nếu thiếu;
- copy `factory/` vào repo;
- viết `factory/checks.sh` từ các lệnh lint, typecheck, test, build mà nó tìm
  thấy trong `package.json`, `Makefile`, `pyproject.toml`, CI;
- đặt `base_branch` và `merge_method` trong `factory/config.json`;
- thêm mục "Software factory" vào `AGENTS.md` (hoặc `CLAUDE.md`), gồm ghi chú
  cho các agent: dự án dùng để làm gì, chỗ nhạy cảm về bảo mật, design token,
  loại người dùng, những gì luôn cần con người duyệt;
- thêm `/factory/jobs/` và `/.worktrees/` vào `.gitignore`;
- thêm vào `.gitattributes` để các script giữ kết thúc dòng LF (CRLF làm hỏng
  dòng shebang trên Windows);
- nếu máy chỉ có lệnh `python` mà không có `python3` chạy được, sửa dòng đầu
  của 3 script trong `factory/bin/` sang `python`;
- tạo ba label `factory`, `factory:needs-info`, `factory:needs-human` trên
  GitHub;
- chạy thử `checks.sh` trên nhánh hiện tại, rồi commit.

Claude sẽ hỏi trước khi push. **Bạn cần push commit này lên nhánh mặc định**
(thường là `main`), vì mỗi job tạo nhánh từ `origin/main`.

Nên đọc lại `factory/checks.sh` và phần ghi chú trong `AGENTS.md` sau khi init.
Đây là hai chỗ quyết định chất lượng kết quả: `checks.sh` là tiêu chuẩn mà mọi
PR phải đạt, còn `AGENTS.md` là thứ mọi agent đọc để hiểu dự án.

---

## 5. Sử dụng hằng ngày

### Đưa việc vào hàng đợi

Gắn label `factory` cho issue trên GitHub. Chỉ issue có label này mới được xử
lý. Chỉ người có quyền triage hoặc write mới gắn được label, nên label chính là
ranh giới tin cậy.

Viết issue rõ ràng: cần gì, tại sao, và thế nào là xong. Issue càng cụ thể,
intake càng ít phải hỏi lại.

### Các lệnh

```
/kaiz-factory:factory run          xử lý mọi issue có label factory
/kaiz-factory:factory run 12       chỉ xử lý issue #12
/kaiz-factory:factory <bất kỳ>     hỏi, góp ý, hoặc tạo tính năng mới
```

Ví dụ cho dạng `<bất kỳ>`:

```
/kaiz-factory:factory job nào đang chờ tôi?
/kaiz-factory:factory issue 12 tốn bao nhiêu tiền?
/kaiz-factory:factory tại sao job 003 bị chuyển cho người duyệt?
/kaiz-factory:factory thêm nút xuất CSV ở trang báo cáo
```

Câu cuối sẽ tạo một issue mới có label `factory` rồi chạy luôn.

### Trong khi chạy

Phiên Claude chạy lệnh trở thành **bộ điều phối**. Nó chạy tối đa
`concurrency` job cùng lúc (mặc định 3) và in một dòng cho mỗi lần chuyển bước,
ví dụ:

```
004-dark-mode #12: gate PASS → reviewing (code, ux, ui)
```

Hãy để phiên đó mở cho đến khi chạy xong. Nếu lỡ tắt, chạy lại
`/kaiz-factory:factory run`, các job sẽ tiếp tục từ bước đang dở.

Khi hết việc, factory in bảng tổng kết: các job đã chạy, chi phí, PR nào chờ
bạn duyệt, câu hỏi nào chờ tác giả issue trả lời.

### Kết quả của một job

| Trạng thái cuối | Ý nghĩa | Bạn cần làm |
|---|---|---|
| `merged` | approver đã duyệt, PR đã merge | không |
| `needs-human` | PR chờ bạn quyết định | xem mục 6 |
| `needs-info` | intake hỏi tác giả issue | chờ tác giả trả lời trên issue |
| `rejected` | intake từ chối | không, hoặc mở lại (mục 6) |

---

## 6. Xử lý job cần con người

### PR có label `factory:needs-human`

Đọc lý do trong comment của approver trên PR. Sau đó chọn một trong ba cách:

- **Đồng ý:** merge PR trên GitHub. Lần chạy sau, factory tự đánh dấu job là
  `merged`.
- **Yêu cầu sửa:** nói với factory cần đổi gì:

  ```
  /kaiz-factory:factory issue 12: đổi màu nút sang màu chính và thêm test cho trường hợp rỗng
  ```

  Factory lưu góp ý vào `feedback-<k>.md`, cấp lại số vòng, và builder làm
  tiếp trên PR đó.
- **Bỏ:**

  ```
  /kaiz-factory:factory bỏ issue 12, không cần tính năng này nữa
  ```

  Factory ghi lý do lên issue, gỡ label, đóng PR. Issue vẫn mở.

### Issue có label `factory:needs-info`

Tác giả trả lời câu hỏi ngay trên issue. Lần chạy sau, job tự quay lại bước
intake. Bạn cũng có thể trả lời thay:

```
/kaiz-factory:factory trả lời issue 12: chỉ cần hỗ trợ file CSV, không cần Excel
```

### Chạy lại một issue đã bị từ chối

Xóa thư mục `factory/jobs/<job-id>` rồi gắn lại label `factory` cho issue.

---

## 7. Dashboard

```bash
cd factory
python3 -m http.server
```

Mở http://localhost:8000/dashboard.html. Dashboard đọc `factory/jobs/` và hiển
thị từng job: bước hiện tại, kết quả review từng vòng, chi phí. Trang tự cập
nhật trong khi factory chạy.

---

## 8. Cấu hình

Các tùy chọn nằm trong `factory/config.json` của từng repo.

| Khóa | Mặc định | Ý nghĩa |
|---|---|---|
| `concurrency` | `3` | số job chạy song song |
| `max_rounds` | `3` | số vòng build → gate → review tối đa mỗi job |
| `base_branch` | `main` | nhánh gốc để tạo nhánh job và merge vào |
| `merge_method` | `merge` | `merge`, `squash` hoặc `rebase` |
| `labels` | `factory`, ... | tên ba label |
| `routing` | low→haiku, medium/high→sonnet | model của reviewer code theo mức rủi ro intake đánh giá |
| `surface_reviewers` | ui: ux+ui, security: security | reviewer thêm khi job đụng giao diện hoặc bảo mật |
| `protected_paths` | `checks.sh`, `config.json` | file job không được sửa; gate FAIL nếu bị sửa |
| `ports` | base 5100, step 10 | cổng dev server; job số n dùng 5100 + 10n |
| `prices_usd_per_mtok` | bảng giá | dùng để tính chi phí trên dashboard |

Lưu ý:

- Không nên thêm thư mục test vào `protected_paths`. Tính năng mới thường phải
  sửa test cũ, và một file test bị khóa sẽ chặn job hoàn toàn. Reviewer code đã
  có nhiệm vụ bắt các test bị làm yếu đi.
- Mẫu trong `protected_paths` theo kiểu fnmatch, nên `*` khớp cả dấu `/`.
- Sửa `factory/config.json` hoặc `factory/checks.sh` thì phải commit và push lên
  nhánh gốc, vì các job đọc chúng từ `origin/<base_branch>`.

---

## 9. Chi phí và an toàn

**Chi phí.** Factory chạy trên gói Claude của bạn. Mỗi job dùng nhiều agent,
phần lớn là Opus. Intake chạy trên Fable, một lần mỗi issue; tùy gói, Fable có
thể tính vào usage credits thay vì phần dùng có sẵn trong gói. Xem chi phí từng
job trên dashboard hoặc hỏi `/kaiz-factory:factory chi phí issue 12`.

**Bắt đầu cẩn thận.** Đặt `"concurrency": 1`, chỉ gắn label cho một hai issue
nhỏ, và đọc mọi PR cho đến khi bạn tin kết quả.

**Giới hạn của factory:**

- chỉ xử lý issue có label `factory`;
- nội dung issue chỉ được đưa cho agent dưới dạng dữ liệu trong `issue.md`,
  không bao giờ nằm trong prompt;
- agent chỉ push nhánh `factory/<job-id>` của job đó;
- chỉ merge qua `factory/bin/job merge`, sau khi chạy lại gate trên code mới
  nhất của nhánh gốc;
- không bao giờ deploy.

**Factory merge PR thật.** Nếu nhánh gốc có branch protection yêu cầu review,
`gh pr merge` sẽ thất bại và job chuyển sang `needs-human`. Đó là cách an toàn
để buộc mọi PR phải qua người duyệt.

---

## 10. Cập nhật và gỡ cài đặt

**Cập nhật plugin** sau khi thư mục hoặc repo plugin có thay đổi:

```
/plugin marketplace update ai-factory
```

Hoặc gỡ rồi cài lại plugin. Bản cập nhật plugin **không** sửa thư mục
`factory/` đã copy vào các repo. Nếu script trong `templates/factory/bin/` thay
đổi, copy lại `bin/` vào từng repo và commit.

**Gỡ plugin:**

```
/plugin uninstall kaiz@ai-factory
/plugin uninstall kaiz-factory@ai-factory
/plugin marketplace remove ai-factory
```

**Gỡ factory khỏi một repo:** xóa `factory/`, `.worktrees/`, mục
"Software factory" trong `AGENTS.md`, hai dòng trong `.gitignore`, và nếu muốn
thì xóa ba label trên GitHub. Xóa các worktree còn sót bằng `git worktree prune`.

---

## 11. Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Factory báo cần chạy init | repo chưa có `factory/` | chạy `/kaiz-factory:init` |
| `python3` mở Microsoft Store hoặc báo không tìm thấy | alias của Windows | làm theo mục 2, phần Windows |
| `gh: command not found` | chưa cài hoặc chưa mở terminal mới | cài `gh`, mở terminal mới, `gh auth login` |
| Mọi job đều gate FAIL | `checks.sh` lỗi ngay trên `main` | chạy `bash factory/checks.sh` ở thư mục gốc repo và sửa script |
| Job không tìm thấy commit init | chưa push commit init lên nhánh gốc | `git push origin main` |
| `job create` từ chối issue | issue chưa có label `factory`, hoặc hết slot | gắn label; chờ job khác xong hoặc tăng `concurrency` |
| Gate FAIL vì protected paths | builder sửa file bị khóa | xem `round-N/checks.md`; nếu cần sửa file đó thì bỏ nó khỏi `protected_paths` |
| Builder không kiểm tra được giao diện | thiếu CLI `agent-browser` | cài `agent-browser`, hoặc kiểm tra giao diện thủ công trên PR |
| Builder không tắt được dev server trên Windows | agent dùng `lsof`, Git Bash không có | tự tắt tiến trình trên cổng của job (5100 + 10n) |
| Không thấy lệnh `/kaiz:...` | plugin chưa bật, hoặc phiên cloud/WSL | `/plugin` để kiểm tra; dùng phiên local |
| Intake báo "Fable requires usage credits" | agent `intake` dùng model Fable, cần usage credits | nạp credits, hoặc đổi dòng `model: fable` trong `agents/intake.md` thành `opus` |
| `job summary` báo "no price for model ..." | model mới chưa có trong bảng giá | thêm model đó vào `prices_usd_per_mtok` trong `factory/config.json` |

Kiểm tra cấu trúc plugin sau khi tự sửa:

```bash
claude plugin validate d:/ai-factory-plugin
```

Xem trạng thái một job: `cat factory/jobs/<job-id>/job.json`. Mọi file của
job (intake, spec, build, review từng vòng, decision) nằm trong cùng thư mục đó.

---

## 12. Phân tích ticket cục bộ (không cần GitHub)

Ngoài pipeline GitHub, plugin còn một chế độ **chỉ phân tích**. Bạn viết ticket
thành file trong repo, và một nhóm agent phân tích nó dựa trên codebase thật
rồi viết bộ tài liệu thiết kế. Chế độ này không sửa code, không tạo nhánh,
không commit, không cần GitHub, `gh` hay `/kaiz-factory:init`.

### Tạo ticket

```
<repo>/
└── .issues/
    └── 123/                 tên thư mục là mã ticket: 123, PROJ-42, ...
        ├── ticket.md        nội dung yêu cầu (bắt buộc)
        └── ...              ảnh chụp, log, ghi chú thêm (tùy chọn)
```

Viết `ticket.md` như một issue tốt: cần gì, tại sao, thế nào là xong, ràng
buộc nếu có. Tài liệu đầu ra được viết bằng ngôn ngữ của `ticket.md`.

Ví dụ:

```markdown
# Thêm lệnh xuất báo cáo CSV

Người dùng cần tải báo cáo doanh thu theo tháng dưới dạng CSV từ trang
/reports. File gồm ngày, mã đơn, khách hàng, tổng tiền. Chỉ admin được tải.
```

### Chạy

```
/kaiz:analyze 123
/kaiz:analyze 123 tập trung vào hiệu năng khi có 1 triệu đơn hàng
/kaiz:analyze
```

- Có mã ticket: phân tích ticket đó. Phần chữ phía sau mã được chuyển nguyên
  văn cho mọi agent như yêu cầu bổ sung.
- Không có mã: phân tích lần lượt mọi ticket chưa có kết quả, hoặc có
  `ticket.md` mới hơn kết quả lần trước.

### Kết quả

```
.issues/123/output/
├── 00-summary.md              tổng kết, mục lục, mâu thuẫn tìm thấy, câu hỏi còn mở
├── 01-assessment.md           GO / NEEDS-INFO / NO-GO, phạm vi, rủi ro, bản đồ codebase
├── 02-impact-analysis.md      file cần sửa, nơi phụ thuộc, hợp đồng API/schema, migration
├── 03-data-flow.md            luồng dữ liệu hiện tại và sau thay đổi (sơ đồ mermaid)
├── 04-tech-spec.md            tiêu chí nghiệm thu và thiết kế kỹ thuật
├── 05-implementation-plan.md  các bước triển khai theo từng file
├── 06-test-plan.md            test case gắn với từng tiêu chí nghiệm thu
├── 07-security.md             rủi ro bảo mật và yêu cầu cho phần triển khai
├── 08-performance.md          hiệu năng: đường chạy nóng, chi phí, ngân sách, cách đo
└── approval.md                quyết định duyệt của bạn (do /kaiz:approve ghi, xem bên dưới)
```

Nên đọc `00-summary.md` trước. Dòng đầu cho biết kết quả tổng:

| `ANALYSIS:` | Ý nghĩa |
|---|---|
| `COMPLETE` | tài liệu đầy đủ, nhất quán và bám đúng code |
| `GAPS` | dùng được, nhưng mục "Issues found" liệt kê vấn đề cần xem |
| `STOPPED` | ticket bị đánh giá NO-GO; lý do nằm trong 00-summary và 01-assessment |

Với ticket `NEEDS-INFO`, phân tích vẫn chạy hết dựa trên các giả định ghi
trong 01-assessment. Trả lời câu hỏi bằng cách bổ sung vào `ticket.md` rồi
chạy lại.

### Phân tích gắn với codebase như thế nào

Mỗi khẳng định về code hiện có phải kèm trích dẫn dạng `đường/dẫn/file.ts:42`
hoặc `đường/dẫn/file.ts:40-58`. Có ba lớp kiểm tra:

1. Mỗi agent phải đọc đoạn code trước khi trích dẫn, và ghi những gì chỉ suy
   luận (không đọc được từ code) vào mục **Assumptions**.
2. Agent `ref-checker` kiểm tra mọi trích dẫn: file phải tồn tại trong repo,
   dòng phải nằm trong file, và mọi tài liệu (trừ 00-summary) phải có ít nhất
   một trích dẫn. Trích dẫn hỏng được gửi lại cho agent viết tài liệu đó để
   sửa một lần. Agent này chỉ đọc và chạy lệnh shell đơn giản như `grep` và
   `wc`, không ghi file nào.
3. Agent `analysis-reviewer` đọc lại các trích dẫn quan trọng nhất để xác nhận
   code nói đúng điều tài liệu khẳng định, và kiểm tra các tài liệu khớp nhau:
   kế hoạch sửa đúng các file trong phân tích ảnh hưởng, mọi tiêu chí nghiệm
   thu có test, mọi yêu cầu bảo mật và hiệu năng có trong kế hoạch.

### Duyệt phương án: `/kaiz:approve`

Phân tích chỉ đề xuất. Quyết định là của bạn, và lệnh này ghi lại quyết định đó
vào `.issues/<ticket>/output/approval.md`:

```
/kaiz:approve 123                          duyệt phương án
/kaiz:approve 123 chỉ làm bước 1 và 2      duyệt kèm điều kiện (ghi nguyên văn)
/kaiz:approve 123 reject thiếu phương án rollback   yêu cầu sửa
/kaiz:approve 123 status                   xem quyết định đang lưu
```

Lệnh trình bày bản tóm tắt để bạn quyết định: kết luận, rủi ro, kích thước,
mức bảo mật và hiệu năng, phương án đề xuất, các vấn đề và câu hỏi còn mở.

- **Không duyệt được** khi phân tích là `STOPPED`, kết luận là NO-GO, hoặc
  tech spec bị `blocked`. Lúc đó chỉ ghi được yêu cầu sửa.
- **Phải xác nhận lại** khi phân tích là `GAPS`, còn câu hỏi mở, kết luận là
  NEEDS-INFO, bảo mật hoặc hiệu năng ở mức `high`, hoặc `ticket.md` mới hơn
  kết quả. Lệnh liệt kê từng điểm và hỏi bạn có duyệt tiếp không. Không xác
  nhận thì không ghi gì.
- Kết quả có ba loại: `APPROVED`, `APPROVED-WITH-CONDITIONS`,
  `CHANGES-REQUESTED`. Với yêu cầu sửa, lệnh gợi ý chạy lại
  `/kaiz:analyze 123 <lý do>` để lý do đó làm ghi chú cho lần phân tích mới.
- Quyết định gắn với bản phân tích hiện tại. Chạy lại `/kaiz:analyze` thì
  `approval.md` đi theo `output-<ngày-giờ>/` cũ, và bản phân tích mới cần được
  duyệt lại.

Lệnh chỉ ghi lại quyết định, không bắt đầu làm gì và không sửa code.

### Chạy lại

Khi chạy lại một ticket đã có kết quả, thư mục `output/` cũ được đổi tên thành
`output-<ngày-giờ>/` để giữ lại, rồi phân tích mới được ghi vào `output/`.

### Từ phân tích sang code

Chế độ phân tích không viết code. Để build, tạo một GitHub issue có label
`factory` (có thể dán nội dung `04-tech-spec.md` vào), rồi chạy
`/kaiz-factory:factory run <số-issue>` trên repo đã chạy init (cần cài plugin
`kaiz-factory`). Hoặc đưa
`05-implementation-plan.md` cho Claude và làm theo từng bước.

### Chi phí

Mỗi ticket dùng 9 agent: 4 trên Opus (đánh giá, bảo mật, tech spec, review) và
5 trên Sonnet (ảnh hưởng, data flow, hiệu năng, test, kiểm tra trích dẫn), cộng
thêm lượt sửa trích dẫn nếu cần. `/kaiz:approve` chỉ dùng phiên hiện tại, không
chạy agent nào. Chế độ này không dùng Fable.
