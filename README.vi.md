# Fabric Engineering Skills

Bộ agent skill biến bất kỳ repo nào thành một **Fabric brain** ("bộ não thứ hai" cho AI): một folder mà AI đọc ở đầu mỗi phiên, nên nó đã biết sẵn các project Microsoft Fabric, naming convention, guardrail của bạn và các tính năng Fabric mới nhất. Bạn không bao giờ phải giải thích lại lần thứ hai.

[English](./README.md)

Dùng được với Claude Code, GitHub Copilot, Codex, Cursor và Gemini CLI. Kiến thức nằm trong file thường (`AGENTS.md` + `reference/`), không nằm trong một tool nào, nên đổi tool thì bạn vẫn mang theo được.

## Tại sao

Điểm nghẽn khi dùng AI để phát triển trên Fabric không còn là độ thông minh của model nữa, mà là **context**. Một phiên chat mới không biết workspace, naming convention, kiến trúc medallion hay quyết định team bạn đưa ra tháng trước. Nên nó trả lời chung chung, bạn phải sửa, và ngày mai nó quên sạch.

Cách sửa giống như onboard một consultant mới: đưa cho họ một bộ tài liệu. Một Fabric brain có bốn phần:

| Phần | File | Vai trò |
| --- | --- | --- |
| **File chỉ dẫn** | `AGENTS.md` (+ các file trỏ một dòng: `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`) | Cách agent hành xử: guardrail, quy tắc cố định, kiến thức nằm ở đâu |
| **File tham chiếu** | `reference/environment.md`, `naming-conventions.md`, `fabric-cli.md`, `architecture/*.md` | Những gì bạn biết: tenant, convention, pattern |
| **Kết nối** | Fabric CLI `fab`, và trong `.mcp.json` hai server bắt buộc **Microsoft Learn MCP** và **Fabric MCP** | Thông tin sống: tài liệu mới nhất, schema item thật, OneLake, và khả năng tạo và chạy item trong Fabric |
| **Workflow** | các skill như trong repo này | Những việc bạn lặp lại hằng ngày |

## Bắt đầu nhanh

### 1. Cài skill

**Claude Code**

```bash
claude plugin marketplace add DKSang/fabric-engineering-skills
claude plugin install fabric-engineering-skills@fabric-engineering
```

**Codex, Copilot, Cursor và các agent khác**

```bash
npx skills@latest add DKSang/fabric-engineering-skills
```

### 2. Chạy `/setup-fabric-engineering-skills`

Chạy một lần trong repo bạn muốn biến thành Fabric brain. Skill sẽ:

1. **Khám phá** repo và máy của bạn: file chỉ dẫn hiện có, cấu hình MCP, folder item Fabric, và đã cài Python, `fab`, Node, `az` chưa
2. **Hỏi** vài câu, mỗi lần một câu, câu nào cũng có đáp án đề xuất:
   - bạn dùng AI tool nào
   - agent được sửa những workspace nào (còn lại chỉ đọc)
   - kết nối MCP server nào
   - `fab` đăng nhập bằng identity nào
3. **Cho xem bản nháp** mọi thứ sẽ ghi, bạn sửa được trước khi ghi
4. **Ghi** `AGENTS.md`, các file trỏ, `reference/`, `data/`, và gộp MCP server và permission rule vào cấu hình sẵn có
5. **Cài** Node.js, Azure CLI và Fabric CLI nếu chưa có, và kết nối hai MCP server bắt buộc: **Microsoft Learn MCP** (tài liệu mới nhất) và **Fabric MCP** (schema item, API spec, OneLake; mặc định chỉ đọc để mọi thay đổi đều đi qua `fab`). Các Fabric MCP khác là tuỳ chọn
6. **Giao phần đăng nhập cho bạn**: bạn tự chạy `fab auth login` và `az login` trong terminal của mình. Agent không bao giờ thấy mật khẩu hay secret
7. **Xác minh** (chỉ đọc): đã đăng nhập, `fab` và `az` cùng tenant, thấy workspace, cả hai MCP server trả lời thật. Kết quả là bảng pass/fail, kèm cách sửa cho từng lỗi

MCP server mới chỉ được nạp trong phiên mới, nên khởi động lại agent rồi chạy:

```
/setup-fabric-engineering-skills verify
```

### 3. Bắt đầu làm việc

Mở phiên mới và yêu cầu việc Fabric mà không cần nhắc lại convention:

> Set up my metadata-driven bronze layer for the orders data in my dev workspace and walk me through what you built.

Agent đọc `AGENTS.md`, lấy quy tắc đặt tên và kiến trúc từ `reference/`, kiểm tra hành vi Fabric hiện tại với Microsoft Learn, chỉ build trong workspace bạn cho phép, rồi đề xuất test end-to-end. Mỗi khi bạn giải thích điều gì mới, nó ghi lại vào `reference/`, nên bộ não thông minh hơn sau mỗi phiên.

## An toàn

Agent hành động dưới danh nghĩa identity đăng nhập vào `fab`. Guardrail bằng chữ giúp nó tuân thủ, nhưng **identity mới là thứ thật sự giới hạn nó**.

- Nên dùng **service principal** chỉ có quyền trên workspace dev. Nếu dùng tài khoản của bạn mà bạn là Fabric admin, agent thấy mọi thứ bạn thấy; hãy dùng tenant playground.
- Lệnh `fab` chỉ đọc chạy tự do; lệnh nào có thể thay đổi Fabric đều hỏi bạn trước.
- Workflow an toàn nhất: để agent sửa item definition trong repo đã kết nối Git, còn bạn tự sync lên Fabric.

## Skill

- **[setup-fabric-engineering-skills](./skills/setup/setup-fabric-engineering-skills/SKILL.md)** (người dùng gọi): biến repo thành Fabric brain, cài CLI và MCP, hướng dẫn đăng nhập, rồi xác minh mọi kết nối.
- **[fabric-brain](./skills/brain/fabric-brain/SKILL.md)** (agent tự gọi): đọc các file `reference/` liên quan trước khi làm việc Fabric, và ghi lại mọi điều lâu dài bạn giải thích hoặc sửa (convention, môi trường, lỗi đã gặp, thuật ngữ nghiệp vụ) vào đúng file, ngay trong lượt đó. Sở hữu bố cục và định dạng của `reference/`.
- **[document-fabric-workspace](./skills/brain/document-fabric-workspace/SKILL.md)** (người dùng gọi): lập danh mục workspace vào `reference/workspaces/<ws>.md` (item, bảng và schema, notebook và pipeline làm gì, lineage). Quét tăng dần: file state lưu fingerprint (ID item, hash definition trong repo, thời điểm sửa bảng) nên lần chạy sau chỉ đọc cái mới, đã đổi hoặc đã cũ. Chỉ đọc, không ghi vào Fabric.
- **[fabric-retro](./skills/brain/fabric-retro/SKILL.md)** (người dùng gọi): chạy trước khi đóng phiên. Tìm lời sửa sai, bài học, sự thật chưa lưu và dòng đã cũ trong `reference/`, đề xuất từng thay đổi kèm bằng chứng, chỉ áp dụng cái bạn chọn.
- **[build-in-fabric](./skills/build/build-in-fabric/SKILL.md)** (agent tự gọi): biến yêu cầu như "dựng bronze layer cho dữ liệu orders trong workspace dev" thành item chạy được: đọc convention, tra định dạng mới nhất trên Fabric MCP và Microsoft Learn, trình kế hoạch dry-run chờ bạn đồng ý, chỉ build trong workspace được phép (trực tiếp bằng `fab`, hoặc ghi definition vào repo đã kết nối Git), xác minh, rồi chạy test end-to-end kiểm tra dữ liệu và tự sửa lỗi.

Các skill tiếp theo (`fabric-item-definitions`, `fabric-guardrails`) nằm trong [roadmap](./README.md#roadmap).

## Liên quan

- [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric): skill workload của Microsoft (Spark, SQL, KQL, semantic model, ...). Bổ sung cho nhau: repo này dựng *context của bạn*, repo của Microsoft dạy các workload. Bước setup có thể cài plugin của họ giúp bạn.
- Lấy cảm hứng từ video [My AI Setup for Microsoft Fabric: Never Explain Yourself Twice](https://youtu.be/5-sXBbBJbAk) của Aleksi Partanen, cấu trúc theo [mattpocock/skills](https://github.com/mattpocock/skills).
