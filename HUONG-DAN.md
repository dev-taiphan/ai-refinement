# Hướng dẫn cài đặt và sử dụng ai-factory

ai-factory là một marketplace cho Claude Code, gồm **hai plugin** độc lập:

| Plugin | Lệnh | Dùng để | Cần gì |
|---|---|---|---|
| `kaiz` | `/kaiz:analyze`, `/kaiz:approve` | Phân tích một ticket viết trong repo, dựa trên codebase thật, ra bộ tài liệu thiết kế rồi ghi lại quyết định duyệt của bạn. **Không sửa code.** | chỉ Claude Code |
| `kaiz-factory` | `/kaiz-factory:init`, `/kaiz-factory:factory` | Biến GitHub issue có label `factory` thành pull request: đánh giá, viết spec, viết code, kiểm thử, review, merge. | `gh`, Python, Git Bash |

Hai plugin dùng riêng hoặc dùng cùng nhau. Chỉ cần phân tích ticket thì bỏ qua
mọi phần về `gh`, Python và `kaiz-factory`.

## Mục lục

- **Phần A. Cài đặt**
  1. [Chuẩn bị máy](#1-chuẩn-bị-máy)
  2. [Cài plugin](#2-cài-plugin)
- **Phần B. Plugin kaiz: phân tích ticket**
  3. [Tạo ticket](#3-tạo-ticket)
  4. [Chạy phân tích](#4-chạy-phân-tích)
  5. [Đọc kết quả](#5-đọc-kết-quả)
  6. [Phân tích bám codebase như thế nào](#6-phân-tích-bám-codebase-như-thế-nào)
  7. [Duyệt phương án](#7-duyệt-phương-án)
  8. [Từ phân tích sang code](#8-từ-phân-tích-sang-code)
- **Phần C. Plugin kaiz-factory: GitHub issue thành pull request**
  9. [Cách pipeline hoạt động](#9-cách-pipeline-hoạt-động)
  10. [Cài factory vào một repo](#10-cài-factory-vào-một-repo)
  11. [Sử dụng hằng ngày](#11-sử-dụng-hằng-ngày)
  12. [Xử lý job cần con người](#12-xử-lý-job-cần-con-người)
  13. [Dashboard](#13-dashboard)
  14. [Cấu hình](#14-cấu-hình)
- **Phần D. Vận hành**
  15. [Chi phí và an toàn](#15-chi-phí-và-an-toàn)
  16. [Cập nhật và gỡ cài đặt](#16-cập-nhật-và-gỡ-cài-đặt)
  17. [Chia sẻ và xuất bản](#17-chia-sẻ-và-xuất-bản)
  18. [Xử lý sự cố](#18-xử-lý-sự-cố)

---

# Phần A. Cài đặt

## 1. Chuẩn bị máy

### Yêu cầu theo plugin

| Công cụ | `kaiz` | `kaiz-factory` | Kiểm tra |
|---|---|---|---|
| Claude Code 2.1.257 trở lên | cần | cần | `claude --version` |
| Git | nên có | cần | `git --version` |
| Git Bash (đi kèm Git for Windows) | không | cần | |
| Python 3.10 trở lên | không | cần | `python3 --version` |
| GitHub CLI `gh`, đã đăng nhập | không | cần | `gh auth status` |

Tài khoản GitHub trong `gh` phải có quyền push vào repo và quản lý label.

Nơi chạy được: Claude Code ở terminal, extension VS Code và các phiên **local**
của ứng dụng Claude Desktop (tab Code). Không chạy trong phiên cloud, phiên WSL
hay ứng dụng chat claude.ai.

### Windows (chỉ cần cho `kaiz-factory`)

**GitHub CLI:**

```powershell
winget install --id GitHub.cli
gh auth login
```

Mở terminal mới sau khi cài để PATH được cập nhật.

**Lệnh `python3`.** Python cài từ python.org chỉ có `python.exe`, còn `python3`
trên Windows thường trỏ tới alias của Microsoft Store và không chạy được
script. Có hai cách:

- Để `/kaiz-factory:init` tự xử lý: nếu `python3` không chạy được mà `python`
  chạy được, nó sửa dòng đầu của ba script trong `factory/bin/` sang `python`.
- Hoặc sửa từ gốc: tắt alias trong Settings → Apps → Advanced app settings →
  App execution aliases (tắt `python.exe` và `python3.exe` của App Installer),
  rồi tạo bản sao `python3.exe` (đổi `Python314` cho đúng phiên bản):

  ```powershell
  $py = "$env:LOCALAPPDATA\Programs\Python\Python314"
  Copy-Item "$py\python.exe" "$py\python3.exe"
  ```

  Mở terminal mới và chạy `python3 --version`. Lệnh phải in ra phiên bản Python
  chứ không mở Microsoft Store.

**Git Bash.** Các script và `checks.sh` chạy bằng bash. Git for Windows đã kèm
Git Bash, và Claude Code trên Windows dùng nó để chạy lệnh.

### macOS và Linux (chỉ cần cho `kaiz-factory`)

```bash
brew install gh        # hoặc theo hướng dẫn tại https://cli.github.com
gh auth login
python3 --version      # thường đã có sẵn
```

## 2. Cài plugin

### Cách A: từ thư mục trên máy

Gõ trong Claude Code:

```
/plugin marketplace add d:/ai-factory-plugin
/plugin install kaiz@ai-factory
/plugin install kaiz-factory@ai-factory
```

Chỉ cài plugin bạn cần.

### Cách B: từ GitHub (để chia sẻ cho người khác)

Đẩy thư mục này lên một repo GitHub (xem mục 17), rồi người dùng gõ:

```
/plugin marketplace add your-org/ai-factory-plugin
/plugin install kaiz@ai-factory
/plugin install kaiz-factory@ai-factory
```

Nếu repo là private, người cài phải có quyền đọc repo đó. Cũng có thể cài từ
shell thay vì trong phiên Claude:

```bash
claude plugin marketplace add your-org/ai-factory-plugin
claude plugin install kaiz@ai-factory
claude plugin install kaiz-factory@ai-factory
```

### Chọn phạm vi cài

Khi chạy `/plugin install`, Claude Code hỏi phạm vi:

- **User:** dùng cho mọi project trên máy, và dùng chung giữa terminal, VS Code
  và Desktop.
- **Project:** ghi vào `.claude/settings.json` của repo, nên cả nhóm cùng được
  nhắc cài khi mở repo đó.

### Kiểm tra

Gõ `/plugin` và xem `kaiz` (và `kaiz-factory` nếu cài) có trong danh sách. Gõ
`/` sẽ thấy `/kaiz:analyze`, `/kaiz:approve`, `/kaiz-factory:init` và
`/kaiz-factory:factory`. Sau khi cài hoặc cập nhật, khởi động lại Claude Code
hoặc chạy `/reload-plugins` để nhận bản mới.

### Dùng thử không cài

```bash
claude --plugin-dir d:/ai-factory-plugin/plugins/kaiz
```

Plugin chỉ có hiệu lực trong phiên đó.

---

# Phần B. Plugin kaiz: phân tích ticket

Bạn viết ticket thành file trong repo. Một nhóm agent đọc codebase, rồi viết bộ
tài liệu thiết kế vào thư mục `output/` cạnh ticket. Bạn đọc, rồi quyết định
duyệt hay yêu cầu sửa. Plugin này **không bao giờ sửa code**, không tạo nhánh,
không commit, không cần GitHub.

## 3. Tạo ticket

Ở thư mục gốc của repo (nơi có `.git`, hoặc thư mục bạn đang mở nếu không phải
repo git):

```
<repo>/
└── .issues/
    └── 123/                 tên thư mục là mã ticket: 123, PROJ-42, ...
        ├── ticket.md        nội dung yêu cầu (bắt buộc)
        └── ...              ảnh chụp, log, ghi chú thêm (tùy chọn)
```

Mọi file khác trong thư mục ticket (ngoài `output/`) cũng được agent đọc như
tài liệu kèm theo.

### Cách viết ticket tốt

Ticket càng cụ thể thì phân tích càng ít phải dựa vào giả định. Nên có:

- **Cần gì:** hành vi mong muốn, nói theo cách người dùng thấy.
- **Tại sao:** vấn đề đang gặp, để agent chọn đúng hướng khi có nhiều cách.
- **Thế nào là xong:** kết quả quan sát được.
- **Ràng buộc:** quy mô dữ liệu, độ trễ chấp nhận được, thứ không được đụng tới,
  thời hạn. Quy mô và độ trễ đặc biệt quan trọng, vì đánh giá hiệu năng lấy
  chúng làm mức thiết kế.

Ví dụ `.issues/123/ticket.md`:

```markdown
# Xuất báo cáo doanh thu theo tháng ra CSV

Người dùng admin cần tải báo cáo doanh thu theo tháng dưới dạng CSV từ trang
/reports. File gồm: ngày, mã đơn, khách hàng, tổng tiền.

- Chỉ admin được tải.
- Một tháng có tới khoảng 1 triệu đơn; tải xong trong 30 giây.
- Không thêm thư viện mới nếu không thật cần.
```

Ngôn ngữ nào cũng được. **Tài liệu đầu ra viết bằng ngôn ngữ của `ticket.md`.**

Bạn có thể commit `.issues/` vào repo để cả nhóm đọc, hoặc thêm vào
`.gitignore` nếu chỉ dùng cá nhân.

## 4. Chạy phân tích

```
/kaiz:analyze 123                      phân tích ticket 123
/kaiz:analyze 123 <ghi chú>            kèm yêu cầu bổ sung cho các agent
/kaiz:analyze                          mọi ticket chưa phân tích hoặc đã đổi
```

- **Ghi chú:** phần chữ sau mã ticket được chuyển nguyên văn cho mọi agent. Ví
  dụ `/kaiz:analyze 123 ưu tiên phương án không đổi schema DB`.
- **Không có mã ticket:** phân tích lần lượt từng ticket chưa có
  `output/00-summary.md`, hoặc có `ticket.md` mới hơn kết quả lần trước.
  Mỗi lần chỉ phân tích một ticket.

### Quy trình bên trong

| Bước | Agent (model) | Việc |
|---|---|---|
| 1 | `ticket-analyst` (Opus) | đọc ticket và code, kết luận GO / NEEDS-INFO / NO-GO, vẽ bản đồ codebase |
| 2 | `impact-analyst`, `dataflow-analyst`, `security-analyst` (Opus), `performance-analyst` (Sonnet) | chạy **song song**: ảnh hưởng, luồng dữ liệu, bảo mật, hiệu năng |
| 3 | `tech-spec-writer` (Opus) | viết tech spec và kế hoạch triển khai từ 4 phân tích trên |
| 4 | `test-planner` (Sonnet) | lập kế hoạch test theo framework sẵn có của dự án |
| 5 | `ref-checker` (Sonnet) | kiểm tra mọi trích dẫn code; trích dẫn hỏng được gửi lại cho tác giả tài liệu sửa một lần |
| 6 | `analysis-reviewer` (Opus) | đọc lại, đối chiếu các tài liệu với nhau, viết tổng kết |

Nếu bước 1 kết luận NO-GO, hoặc bước 3 báo spec bị chặn, quy trình dừng sớm
và tổng kết ghi `STOPPED`.

Mỗi lần chuyển bước, Claude in một dòng trạng thái. Hãy để phiên mở đến khi
xong; thường mất vài phút trở lên, tùy độ lớn của repo.

### Quyền chạy lệnh

Agent `ref-checker` dùng vài lệnh shell chỉ-đọc (`grep`, `wc`) để kiểm tra
trích dẫn. Nếu Claude Code hỏi quyền chạy các lệnh này, bạn có thể cho phép
hoặc thêm vào danh sách cho phép để khỏi bị hỏi lại. Các agent khác chỉ đọc
repo và ghi file trong `.issues/<mã>/output/`.

### Chạy lại

Khi chạy lại một ticket đã có kết quả, thư mục `output/` cũ được đổi tên thành
`output-<ngày-giờ>/` để giữ lại (cùng với `approval.md` nếu có), rồi phân tích
mới được ghi vào `output/`. Xóa các thư mục `output-...` cũ nếu không cần.

## 5. Đọc kết quả

Kết quả nằm trong `.issues/<mã>/output/`:

| File | Nội dung | Dòng đầu |
|---|---|---|
| `00-summary.md` | tổng kết, mục lục, mâu thuẫn tìm thấy, câu hỏi còn mở, bước tiếp theo | `ANALYSIS:` |
| `01-assessment.md` | tóm tắt ticket, phạm vi, bản đồ codebase, cách code đang chạy | `VERDICT`, `RISK`, `SURFACES`, `SIZE` |
| `02-impact-analysis.md` | file cần sửa, file mới, nơi phụ thuộc, hợp đồng API/schema, migration, rollback | `IMPACT:` |
| `03-data-flow.md` | luồng dữ liệu trước và sau (có sơ đồ), mô hình dữ liệu, ranh giới tin cậy, xử lý lỗi | `FLOW:` |
| `04-tech-spec.md` | tiêu chí nghiệm thu, thiết kế, phương án đã cân nhắc | `SPEC:` |
| `05-implementation-plan.md` | các bước làm theo thứ tự, mỗi bước nêu file, thay đổi và cách kiểm tra | `PLAN:` |
| `06-test-plan.md` | test case gắn với từng tiêu chí nghiệm thu, kiểm tra hiệu năng | `TESTS:` |
| `07-security.md` | rủi ro bảo mật và yêu cầu cho phần triển khai | `SECURITY:` |
| `08-performance.md` | đường chạy nóng, chi phí, ngân sách, cách đo | `PERFORMANCE:` |
| `approval.md` | quyết định duyệt của bạn, do `/kaiz:approve` ghi (mục 7) | `DECISION:` |

### Thứ tự nên đọc

1. **`00-summary.md`** trước tiên: kết quả tổng, các vấn đề, câu hỏi còn mở.
2. `01-assessment.md`: ticket được hiểu thế nào, có nên làm không.
3. `04-tech-spec.md` và `05-implementation-plan.md`: phương án và các bước.
4. `07-security.md`, `08-performance.md`: các rủi ro cần cân nhắc.
5. Các file còn lại khi cần kiểm chứng.

### Ý nghĩa các giá trị chính

| Trường | Giá trị |
|---|---|
| `ANALYSIS` | `COMPLETE`: đầy đủ, nhất quán, bám đúng code. `GAPS`: dùng được nhưng mục "Issues found" nêu vấn đề cần xem. `STOPPED`: ticket bị NO-GO hoặc spec bị chặn. |
| `VERDICT` | `GO`: làm được. `NEEDS-INFO`: có quyết định chỉ tác giả ticket trả lời được; phân tích vẫn chạy hết dựa trên giả định ghi trong file. `NO-GO`: không nên làm, lý do nằm trong file. |
| `RISK` | `low`: gọn, dễ kiểm chứng. `medium`: nhiều module hoặc code dùng chung. `high`: dữ liệu, tiền, xác thực, migration, đồng thời, khó hoàn tác. |
| `SIZE` | `S`: vài file. `M`: một module. `L`: nhiều module. `XL`: nên tách nhỏ, cách tách ghi trong phần Scope. |
| `SECURITY`, `PERFORMANCE` | `none`, `low`, `medium`, `high` |

### Xử lý theo từng kết quả

- **`GAPS`:** đọc "Issues found" trong `00-summary.md`. Thường là hai tài liệu
  mâu thuẫn nhau hoặc một khẳng định thiếu căn cứ. Sửa `ticket.md` hoặc chạy
  lại với ghi chú, hoặc chấp nhận có điều kiện khi duyệt.
- **`NEEDS-INFO`:** trả lời các câu hỏi bằng cách bổ sung vào `ticket.md` rồi
  chạy lại `/kaiz:analyze`.
- **`STOPPED`:** đọc lý do trong `00-summary.md`. Nếu bạn không đồng ý, bổ sung
  bối cảnh vào ticket và chạy lại.
- **`SIZE: XL`:** tách ticket theo gợi ý rồi phân tích từng phần.

## 6. Phân tích bám codebase như thế nào

Mỗi khẳng định về code hiện có phải kèm trích dẫn dạng `đường/dẫn/file.ts:42`
hoặc `đường/dẫn/file.ts:40-58`. Có ba lớp kiểm tra:

1. **Agent phân tích** phải đọc đoạn code trước khi trích dẫn, và ghi những gì
   chỉ suy luận vào mục **Assumptions**, kể cả mọi con số ước lượng.
2. **`ref-checker`** kiểm tra mọi trích dẫn: file phải tồn tại trong repo, dòng
   phải nằm trong file, và mọi tài liệu (trừ `00-summary.md`) phải có ít nhất
   một trích dẫn. Agent này chỉ đọc, không ghi file nào.
3. **`analysis-reviewer`** đọc lại các trích dẫn quan trọng nhất để xác nhận
   code nói đúng điều tài liệu khẳng định, và kiểm tra các tài liệu khớp nhau:
   kế hoạch sửa đúng các file trong phân tích ảnh hưởng, mọi tiêu chí nghiệm
   thu có test, mọi yêu cầu bảo mật và hiệu năng có trong kế hoạch và test.

### Giới hạn cần biết

- Nội dung do AI sinh ra từ việc đọc code. Trích dẫn đúng dòng chưa chắc có
  nghĩa kết luận đúng: hãy đọc kỹ **Assumptions** và **Open questions**, đây là
  chỗ agent ghi những gì nó không đọc được từ code.
- Kiểm tra trích dẫn xác nhận file và dòng có thật, không xác nhận ý nghĩa.
  Phần xác nhận ý nghĩa do agent review làm trên các trích dẫn quan trọng nhất,
  không phải trên tất cả.
- Con số hiệu năng chỉ là ước lượng trừ khi có trích dẫn từ repo. Muốn số thật,
  chạy cách đo mà `08-performance.md` nêu.
- Kết quả có thể khác nhau giữa các lần chạy.

## 7. Duyệt phương án

Phân tích chỉ đề xuất, quyết định là của bạn. `/kaiz:approve` ghi lại quyết định
đó vào `.issues/<mã>/output/approval.md`:

```
/kaiz:approve 123                                   duyệt phương án
/kaiz:approve 123 chỉ làm bước 1 và 2               duyệt kèm điều kiện
/kaiz:approve 123 reject thiếu phương án rollback   yêu cầu sửa
/kaiz:approve 123 status                            xem quyết định đang lưu
```

Lệnh hiện một bản tóm tắt để bạn quyết định: kết luận, rủi ro, kích thước, mức
bảo mật và hiệu năng, phương án đề xuất, các vấn đề và câu hỏi còn mở.

- **Không duyệt được** khi phân tích là `STOPPED`, kết luận là NO-GO, hoặc tech
  spec bị `blocked`. Lúc đó chỉ ghi được yêu cầu sửa.
- **Phải xác nhận lại** khi phân tích là `GAPS`, còn câu hỏi mở, kết luận là
  NEEDS-INFO, bảo mật hoặc hiệu năng ở mức `high`, hoặc `ticket.md` mới hơn kết
  quả. Lệnh liệt kê từng điểm và hỏi bạn có duyệt tiếp không. Không xác nhận
  thì không ghi gì. Điều kiện bạn gõ kèm được ghi nguyên văn vào `approval.md`.
- **Ba loại quyết định:** `APPROVED`, `APPROVED-WITH-CONDITIONS`,
  `CHANGES-REQUESTED`. Với yêu cầu sửa, lệnh gợi ý chạy lại
  `/kaiz:analyze 123 <lý do>` để lý do đó thành ghi chú cho lần phân tích mới.
- **Quyết định gắn với bản phân tích hiện tại.** Chạy lại `/kaiz:analyze` thì
  `approval.md` đi theo thư mục `output-<ngày-giờ>/` cũ, và bản mới cần được
  duyệt lại.

Lệnh chỉ ghi lại quyết định, không bắt đầu làm gì và không sửa code. Nó không
chạy agent nào, chỉ dùng phiên hiện tại.

## 8. Từ phân tích sang code

Sau khi duyệt, có ba đường:

- **Tự làm hoặc nhờ Claude làm** theo `05-implementation-plan.md`, kiểm tra bằng
  các case trong `06-test-plan.md`.
- **Dùng pipeline GitHub:** nếu đã cài `kaiz-factory`, tạo một GitHub issue có
  label `factory` (có thể dán `04-tech-spec.md` vào mô tả) rồi chạy
  `/kaiz-factory:factory run <số-issue>` trên repo đã chạy init (Phần C).
- **Chia nhỏ:** với ticket `XL`, tách theo gợi ý trong `01-assessment.md` rồi
  phân tích và làm từng phần.

---

# Phần C. Plugin kaiz-factory: GitHub issue thành pull request

## 9. Cách pipeline hoạt động

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
nhiều job chạy song song không đụng nhau và thư mục làm việc chính của bạn
không bị thay đổi. Trạng thái job nằm trong `factory/jobs/`, nên nếu phiên
Claude bị tắt giữa chừng, lần chạy sau tiếp tục từ chỗ đã dừng.

Plugin không dùng hook. Builder tự chạy `checks.sh` trước khi kết thúc, và gate
chạy lại sau đó, nên một bản build lỗi vẫn bị chặn trước khi tới reviewer.

## 10. Cài factory vào một repo

Plugin cung cấp agent và lệnh. Mỗi repo cần thêm thư mục `factory/` riêng chứa
script, cấu hình và lệnh kiểm thử của repo đó. Làm **một lần cho mỗi repo**.

1. Mở Claude Code ở thư mục gốc của repo. Repo phải có remote `origin` trên
   GitHub.
2. Chạy:

   ```
   /kaiz-factory:init
   ```

Claude sẽ:

- kiểm tra các yêu cầu ở mục 1 và dừng lại báo lỗi nếu thiếu;
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
  của ba script trong `factory/bin/` sang `python`;
- tạo ba label `factory`, `factory:needs-info`, `factory:needs-human` trên
  GitHub;
- chạy thử `checks.sh` trên nhánh hiện tại, rồi commit.

Claude hỏi trước khi push. **Bạn cần push commit này lên nhánh mặc định**
(thường là `main`), vì mỗi job tạo nhánh từ `origin/main`.

Nên đọc lại `factory/checks.sh` và phần ghi chú trong `AGENTS.md` sau khi init.
Đây là hai chỗ quyết định chất lượng kết quả: `checks.sh` là tiêu chuẩn mà mọi
PR phải đạt, còn `AGENTS.md` là thứ mọi agent đọc để hiểu dự án.

## 11. Sử dụng hằng ngày

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

Câu cuối tạo một issue mới có label `factory` rồi chạy luôn.

### Trong khi chạy

Phiên Claude chạy lệnh trở thành **bộ điều phối**. Nó chạy tối đa
`concurrency` job cùng lúc (mặc định 3) và in một dòng cho mỗi lần chuyển bước:

```
004-dark-mode #12: gate PASS → reviewing (code, ux, ui)
```

Hãy để phiên đó mở cho đến khi chạy xong. Nếu lỡ tắt, chạy lại
`/kaiz-factory:factory run`, các job tiếp tục từ bước đang dở.

Khi hết việc, factory in bảng tổng kết: các job đã chạy, chi phí, PR nào chờ
bạn duyệt, câu hỏi nào chờ tác giả issue trả lời.

### Kết quả của một job

| Trạng thái cuối | Ý nghĩa | Bạn cần làm |
|---|---|---|
| `merged` | approver đã duyệt, PR đã merge | không |
| `needs-human` | PR chờ bạn quyết định | xem mục 12 |
| `needs-info` | intake hỏi tác giả issue | chờ tác giả trả lời trên issue |
| `rejected` | intake từ chối | không, hoặc mở lại (mục 12) |

## 12. Xử lý job cần con người

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

## 13. Dashboard

```bash
cd factory
python3 -m http.server
```

Mở http://localhost:8000/dashboard.html. Dashboard đọc `factory/jobs/` và hiển
thị từng job: bước hiện tại, kết quả review từng vòng, chi phí. Trang tự cập
nhật trong khi factory chạy.

## 14. Cấu hình

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
- Bảng giá khớp **chính xác** theo tên model. Gặp model mới, `job` báo lỗi
  "no price for model ..." cho tới khi bạn thêm model đó vào bảng. Giá của các
  dòng Fable 5-2 và 5 được chép từ bản 5-1 chứ chưa đối chiếu với bảng giá
  chính thức, nên chi phí hiển thị cho Fable có thể lệch.

---

# Phần D. Vận hành

## 15. Chi phí và an toàn

### Chi phí

Cả hai plugin chạy trên gói Claude của bạn.

- **`kaiz`:** mỗi ticket dùng 9 agent: 4 trên Opus (đánh giá, bảo mật, tech
  spec, review) và 5 trên Sonnet (ảnh hưởng, data flow, hiệu năng, test, kiểm
  tra trích dẫn), cộng thêm lượt sửa trích dẫn nếu cần. Không dùng Fable.
  `/kaiz:approve` không chạy agent nào.
- **`kaiz-factory`:** mỗi job dùng nhiều agent, phần lớn là Opus. Intake chạy
  trên Fable, một lần mỗi issue; tùy gói, Fable có thể tính vào usage credits
  thay vì phần dùng có sẵn trong gói. Xem chi phí từng job trên dashboard hoặc
  hỏi `/kaiz-factory:factory chi phí issue 12`.

Cả hai đều gọi nhiều agent trên repo lớn, nên hãy thử trên một ticket nhỏ
trước.

### Bắt đầu cẩn thận với kaiz-factory

Đặt `"concurrency": 1`, chỉ gắn label cho một hai issue nhỏ, và đọc mọi PR cho
đến khi bạn tin kết quả.

### Giới hạn an toàn

`kaiz`:

- agent chỉ đọc repo và chỉ ghi file trong `.issues/<mã>/output/`;
- nội dung ticket được đọc như dữ liệu, không như chỉ dẫn;
- không sửa code, không tạo nhánh, không commit, không dùng GitHub.

`kaiz-factory`:

- chỉ xử lý issue có label `factory`;
- nội dung issue chỉ được đưa cho agent dưới dạng dữ liệu trong `issue.md`,
  không bao giờ nằm trong prompt;
- agent chỉ push nhánh `factory/<job-id>` của job đó;
- chỉ merge qua `factory/bin/job merge`, sau khi chạy lại gate trên code mới
  nhất của nhánh gốc;
- không bao giờ deploy.

**Factory merge PR thật.** Nếu nhánh gốc có branch protection yêu cầu review,
`gh pr merge` thất bại và job chuyển sang `needs-human`. Đó là cách an toàn để
buộc mọi PR phải qua người duyệt.

## 16. Cập nhật và gỡ cài đặt

### Cập nhật plugin

Sau khi thư mục hoặc repo plugin có thay đổi (nhớ tăng `version` trong
`plugin.json` của plugin đã đổi):

```
/plugin marketplace update ai-factory
```

rồi cập nhật plugin hoặc gỡ và cài lại, và khởi động lại Claude Code (hoặc
`/reload-plugins`). Từ shell: `claude plugin marketplace update ai-factory` và
`claude plugin update kaiz@ai-factory`.

Cập nhật `kaiz-factory` **không** sửa thư mục `factory/` đã copy vào các repo.
Nếu script trong `plugins/kaiz-factory/templates/factory/bin/` thay đổi, copy
lại `bin/` vào từng repo và commit.

### Gỡ plugin

```
/plugin uninstall kaiz@ai-factory
/plugin uninstall kaiz-factory@ai-factory
/plugin marketplace remove ai-factory
```

### Gỡ factory khỏi một repo

Xóa `factory/`, `.worktrees/`, mục "Software factory" trong `AGENTS.md`, các
dòng thêm vào `.gitignore` và `.gitattributes`, và nếu muốn thì xóa ba label
trên GitHub. Xóa các worktree còn sót bằng `git worktree prune`.

### Gỡ dữ liệu phân tích

Thư mục `.issues/` là của bạn. Gỡ plugin `kaiz` không xóa nó.

## 17. Chia sẻ và xuất bản

### Cấu trúc repo

```
.claude-plugin/marketplace.json   liệt kê hai plugin
plugins/kaiz/                     ticket analysis: agents/, skills/analyze/, skills/approve/
plugins/kaiz-factory/             pipeline: agents/, skills/factory/, skills/init/, templates/factory/
```

Mỗi thư mục plugin tự đủ: có manifest, icon, README và LICENSE riêng, nên có thể
nộp riêng từng cái.

### Chia sẻ qua marketplace GitHub (không cần duyệt)

1. Tạo repo trống trên GitHub, ví dụ `your-org/ai-factory-plugin`.
2. Đẩy thư mục lên:

   ```bash
   cd d:/ai-factory-plugin
   git add -A
   git status
   git commit -m "Update plugins"
   git push
   ```

   Xem `git status` trước khi commit để chắc không có file ngoài ý muốn
   (`.gitignore` đã chặn `__pycache__/` và `*.pyc`).
3. Người khác cài bằng `/plugin marketplace add your-org/ai-factory-plugin`.

### Nộp lên thư mục chính thức của Anthropic

Thư mục chính thức là danh mục riêng. Đăng ký marketplace trên máy bạn không
đưa plugin vào đó. Theo tài liệu và kết quả validate bạn đã nhận:

1. Vào https://claude.ai/directory/manage, chọn "Submit new" rồi "Plugin
   bundle". Cần gói claude.ai trả phí; với Team hoặc Enterprise, người nộp là
   Owner hoặc có quyền Directory.
2. Nhập repo GitHub và **đường dẫn plugin là `plugins/kaiz`**, bấm Validate.
3. Điền thông tin hiển thị, phần xử lý dữ liệu và tuân thủ, rồi "Submit for
   review". Theo dõi trạng thái ngay trong cổng. Tài liệu không nêu thời gian
   duyệt.

Điều kiện đã gặp khi validate:

- **Chỉ nộp `kaiz`.** Với tổ chức chưa xác minh, cổng chỉ nhận Markdown, text,
  JSON, YAML và ảnh (PNG, JPEG, GIF, WebP, ICO). Nó từ chối script, file bắt
  đầu bằng `#!`, `dashboard.html` và mọi hook kiểu `command`. `kaiz-factory` có
  đủ các thứ đó nên không nộp được; hãy chia sẻ nó qua marketplace GitHub.
- Repo phải **public** trước khi danh sách chính thức hiện ra (private vẫn dùng
  được để kiểm tra và duyệt).
- Cần `author` trong `plugin.json`, icon, README từ 40 từ trở lên và giấy phép.
- Tên plugin không được trùng hoặc dễ nhầm với plugin hay thương hiệu có sẵn.
  Cổng có thể để người duyệt quyết định (policy hold).
- Đừng commit file sinh ra như `__pycache__/`: cổng từ chối chúng.

Muốn hỏi thêm về quy trình, icon hay thời gian duyệt, gửi email tới
directory@anthropic.com hoặc dùng `/feedback`.

### Giấy phép

`LICENSE` hiện là GPL-3.0-only và được ghi trong `plugin.json` của cả hai
plugin. `kaiz-factory` có nguồn gốc từ mã GPLv3 nên cần giữ giấy phép đó. Với
`kaiz` là phần bạn tự phát triển, bạn có thể chọn giấy phép khác bằng cách sửa
`LICENSE` và trường `license` trong `plugins/kaiz/.claude-plugin/plugin.json`.
Hãy xác nhận kỹ với nguồn gốc mã trước khi đổi.

## 18. Xử lý sự cố

### Chung

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Không thấy lệnh `/kaiz:...` hoặc `/kaiz-factory:...` | plugin chưa cài hoặc chưa nạp, hoặc đang ở phiên cloud/WSL | `/plugin` để kiểm tra; khởi động lại hoặc `/reload-plugins`; dùng phiên local |
| Plugin bị lỗi cấu trúc sau khi tự sửa | manifest hoặc file sai chỗ | `claude plugin validate d:/ai-factory-plugin/plugins/kaiz` (hoặc `kaiz-factory`) |

### Với kaiz

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Báo không tìm thấy `ticket.md` | sai đường dẫn hoặc sai thư mục gốc | đặt file ở `<repo>/.issues/<mã>/ticket.md` và mở Claude Code ở thư mục gốc repo |
| Phân tích chạy lâu | repo lớn, nhiều agent chạy tuần tự | chờ; thử trước trên ticket nhỏ |
| Hỏi quyền chạy lệnh nhiều lần | `ref-checker` dùng `grep`, `wc` | cho phép các lệnh chỉ-đọc đó |
| Kết quả `GAPS` | tài liệu mâu thuẫn hoặc thiếu căn cứ | đọc "Issues found" trong `00-summary.md`, sửa ticket hoặc chạy lại với ghi chú |
| Tài liệu viết sai ngôn ngữ | ngôn ngữ theo `ticket.md` | viết lại `ticket.md` bằng ngôn ngữ mong muốn rồi chạy lại |
| `/kaiz:approve` không ghi `approval.md` | cần bạn xác nhận (gaps, câu hỏi mở, mức high, ticket đã đổi) hoặc phân tích `STOPPED` | trả lời xác nhận khi được hỏi, hoặc gõ điều kiện kèm lệnh; xem lý do lệnh in ra |
| `/kaiz:approve` báo cần chạy analyze | chưa có `output/00-summary.md` | chạy `/kaiz:analyze <mã>` trước |

### Với kaiz-factory

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Factory báo cần chạy init | repo chưa có `factory/` | chạy `/kaiz-factory:init` |
| `python3` mở Microsoft Store hoặc báo không tìm thấy | alias của Windows | làm theo mục 1, phần Windows, hoặc để init sửa sang `python` |
| `gh: command not found` | chưa cài hoặc chưa mở terminal mới | cài `gh`, mở terminal mới, `gh auth login` |
| Mọi job đều gate FAIL | `checks.sh` lỗi ngay trên `main` | chạy `bash factory/checks.sh` ở thư mục gốc repo và sửa script |
| Job không tìm thấy commit init | chưa push commit init lên nhánh gốc | `git push origin main` |
| `job create` từ chối issue | issue chưa có label `factory`, hoặc hết slot | gắn label; chờ job khác xong hoặc tăng `concurrency` |
| Gate FAIL vì protected paths | builder sửa file bị khóa | xem `round-N/checks.md`; nếu cần sửa file đó thì bỏ nó khỏi `protected_paths` |
| Builder không kiểm tra được giao diện | thiếu CLI `agent-browser` | cài `agent-browser`, hoặc kiểm tra giao diện thủ công trên PR |
| Builder không tắt được dev server trên Windows | agent dùng `lsof`, Git Bash không có | tự tắt tiến trình trên cổng của job (5100 + 10n) |
| Script lỗi `python3\r` hoặc `bad interpreter` | file bị đổi sang CRLF | thêm `factory/bin/* text eol=lf` vào `.gitattributes` và checkout lại file |
| Intake báo "Fable requires usage credits" | agent `intake` dùng model Fable, cần usage credits | nạp credits, hoặc đổi dòng `model: fable` trong `agents/intake.md` của plugin thành `opus` |
| `job summary` báo "no price for model ..." | model mới chưa có trong bảng giá | thêm model đó vào `prices_usd_per_mtok` trong `factory/config.json` |

Xem trạng thái một job: `cat factory/jobs/<job-id>/job.json`. Mọi file của job
(intake, spec, build, review từng vòng, decision) nằm trong cùng thư mục đó.
