# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Phan Thị Mai Phương
**Nhóm:** C401-C1
**Ngày:** 10-04-2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:* Cosine similarity đo mức độ tương đồng giữa hai vector dựa trên góc giữa chúng, không phải độ dài. Cosine similarity càng cao, hướng hai vector càng giống/trùng nhau - tức là nội dung ngữ nghĩa sẽ càng giống nhau.

**Ví dụ HIGH similarity:**
- Sentence A: The cat plays with a ball.
- Sentence B: A ball is played by the cat.
- Tại sao tương đồng: Vì nội dung giống y hệt nhau, cùng mô tả đối tượng và hành động, chỉ thay đổi từ thể chủ động sang bị động.

**Ví dụ LOW similarity:**
- Sentence A: The cat plays with a ball.
- Sentence B: Outside, there is a downpour.
- Tại sao khác: Nội dung khác hoàn toàn nhau, chủ thể hành động và sự việc đều không có chút liên quan nào.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Nếu dùng Euclidean distance, văn bản dài có thể bị xem là “xa” hơn chỉ vì nhiều từ — không có ý nghĩa. Cosine Similarity giải quyết bằng cách loại bỏ ảnh hưởng độ dài.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
$$
\text{số chunks} = \left\lceil \frac{\text{document length} - chunk\_size}{chunk\_size - overlap} \right\rceil + 1
$$
$$
= \left\lceil \frac{10000 - 500}{500 - 50} \right\rceil + 1
= \left\lceil \frac{9500}{450} \right\rceil + 1
= \left\lceil {21.11} \right\rceil + 1 = 22+1
$$
> *Đáp án:* 23 chunks 

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> chunk_count sẽ tăng từ 23 lên 25. Overlap lớn hơn nhằm giữa ngữ cảnh liên tục giữa các chunk, tránh việc thông tin cắt nhiều làm giảm chất lượng retrieval

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Hệ thống hỗ trợ học tập và tra cứu quy trình khóa học "AI Thực Chiến" (VinUni A20)

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này để hỗ trợ sinh viên tra cứu nhanh các kiến thức, mục tiêu và bước thực hiện trong các bài Lab AI. Việc áp dụng RAG vào kho bài giảng giúp việc học tập trở nên chủ động hơn, đặc biệt khi cần tìm kiếm các lệnh (commands) hoặc quy trình cụ thể qua nhiều ngày học khác nhau.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | day02.md | https://github.com/a20-ai-thuc-chien | 5536 | day: "02", topic: "problem_statement" |
| 2 | day03.md | https://github.com/a20-ai-thuc-chien | 2336 | day: "03", topic: "agent_implementation" |
| 3 | day05.md | https://github.com/a20-ai-thuc-chien | 10591 | day: "05", topic: "product_design" |
| 4 | day06.md | https://github.com/a20-ai-thuc-chien | 14954 | day: "06", topic: "hackathon" |
| 5 | day07.md | https://github.com/a20-ai-thuc-chien | 6628 | day: "07", topic: "embedding_rag" |

### Metadata Schema

| Trường metadata | Kiểu   | Ví dụ giá trị    | Tại sao hữu ích cho retrieval?                     |
| --------------- | ------ | ---------------- | -------------------------------------------------- |
| type            | string | lecture / lab    | Lọc theo loại nội dung (bài giảng lý thuyết hay thực hành) |
| topic           | string | agents, data     | Thu hẹp phạm vi theo chủ đề kỹ thuật               |
| day             | integer| 7                | Tìm kiếm thông tin theo lộ trình thời gian của khóa học |
| priority        | string | high             | Ưu tiên các hướng dẫn quan trọng khi trả về kết quả |
| source          | string | vinuni           | Xác nhận nguồn tin cậy của bài |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| day02.md | FixedSizeChunker (`fixed_size`) | 37 | 198.0 | Một nửa |
| day02.md | SentenceChunker (`by_sentences`) | 7 | 787.5714285714286 | Có |
| day02.md | RecursiveChunker (`recursive`) | 45 | 121.08888888888889 | Có |
| day03.md | FixedSizeChunker (`fixed_size`) | 16 | 192.875 | Hầu hết |
| day03.md | SentenceChunker (`by_sentences`) | 9 | 257.3333333333333 | Có |
| day03.md | RecursiveChunker (`recursive`) | 17 | 135.8235294117647 | Có |
| day05.md | FixedSizeChunker (`fixed_size`) | 71 | 198.46478873239437 | Một nửa |
| day05.md | SentenceChunker (`by_sentences`) | 14 | 752.3571428571429 | Có |
| day05.md | RecursiveChunker (`recursive`) | 79 | 132.40506329113924 | Có |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> Strategy này hoạt động bằng cách thử tách văn bản theo danh sách các dấu phân cách ưu tiên từ lớn đến nhỏ: đoạn văn (\n\n), dòng (\n), câu (. ), từ ( ) và cuối cùng là ký tự rỗng (""). Nó giúp giữ được cấu trúc ngữ nghĩa lớn nhất có thể trước khi phải chia nhỏ thêm để thỏa mãn giới hạn `chunk_size`.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Vì các file này có cấu trúc phân cấp (Header #, ##, ###), việc sử dụng RecursiveChunker với các dấu phân cách như `["\n### ", "\n## ", "\n# ", "\n\n", ". "]` giúp giữ nguyên các đoạn hướng dẫn hoặc tiêu chí chấm điểm đi liền với nhau, tránh bị mất ngữ cảnh quan trọng khi một lệnh code hoặc một định nghĩa bị cắt giữa chừng.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| day02.md | best baseline (SentenceChunker) | 7 | 787.57 | Cao (giữ nguyên ngữ nghĩa câu, dễ match query) |
| day02.md | **của tôi (RecursiveChunker)**  | 45 | 121.09 | Trung bình (chi tiết hơn nhưng dễ vỡ context)  |
| day03.md | best baseline (SentenceChunker) | 9 | 257.33 | Cao (cân bằng giữa độ dài và ngữ nghĩa)        |
| day03.md | **của tôi (RecursiveChunker)**  | 17 | 135.82 | Khá (fine-grained hơn nhưng đôi khi mất ý)     |
| day05.md | best baseline (SentenceChunker) | 14 | 752.36 | Cao (phù hợp nội dung dài, nhiều giải thích)   |
| day05.md | **của tôi (RecursiveChunker)**  | 79 | 132.40 | Trung bình (nhiều chunk nhỏ → noise cao hơn)   |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Dữ liệu của nhóm (markdown) thường có cấu trúc rõ ràng theo đoạn và dòng, không phải plain text liên tục.
RecursiveChunker tận dụng tốt cấu trúc này, giúp giữ nguyên context theo đoạn thay vì cắt cứng như FixedSizeChunker hoặc gom quá dài như SentenceChunker.
Điều này đặc biệt quan trọng cho RAG, vì context rõ ràng sẽ giúp retrieval chính xác hơn.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng regex (?<=[.!?])\s+ để tách câu dựa trên dấu kết thúc (., !, ?) theo sau bởi khoảng trắng, giúp giữ lại dấu câu trong mỗi sentence. Sau đó nhóm các câu theo max_sentences_per_chunk và join lại thành chunk. Có xử lý edge case như text rỗng và loại bỏ khoảng trắng thừa để tránh tạo chunk rỗng.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán ưu tiên tách văn bản theo danh sách separators từ “mạnh” đến “yếu” (paragraph → newline → câu → từ → ký tự), sau đó đệ quy xử lý các đoạn vượt quá chunk_size bằng separator tiếp theo. Ở mỗi bước, các phần nhỏ được gom lại vào buffer sao cho không vượt quá giới hạn kích thước. Base case là khi đoạn hiện tại đủ nhỏ (<= chunk_size) hoặc khi không còn separator nào thì fallback sang cắt cứng theo độ dài.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi document được embed thành vector và lưu dưới dạng record trong in-memory list (_store), bao gồm nội dung, embedding và metadata. Khi search, query cũng được embed thành vector, sau đó tính độ tương đồng (dot product) với tất cả embedding đã lưu. Kết quả được sắp xếp giảm dần theo score và trả về top_k phần tử liên quan nhất.

**`search_with_filter` + `delete_document`** — approach:
> *search_with_filter thực hiện lọc theo metadata trước, chỉ giữ lại các records thỏa điều kiện rồi mới tính similarity trên tập đã lọc. delete_document duyệt qua _store và loại bỏ các record có id trùng với doc_id, sau đó so sánh kích thước trước–sau để trả về True/False.

### KnowledgeBaseAgent

**`answer`** — approach:
> Ddầu tiên hàm retrieve top_k chunks liên quan từ vector store, sau đó nối chúng lại thành một đoạn context duy nhất. Context này được inject trực tiếp vào prompt theo format “Context → Question → Answer” để buộc LLM chỉ dựa vào thông tin đã cung cấp. Cuối cùng, prompt được gửi vào llm_fn để tạo câu trả lời.

### Test Results

```
platform win32 -- Python 3.13.9, pytest-9.0.2, pluggy-1.6.0 -- C:\Program Files\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\E\Learning\Day-07-Lab-Data-Foundations-main
plugins: anyio-4.13.0
collected 42 items                                                                                                                                                       

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                                                              [  2%] 
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                                                                       [  4%] 
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                                                                [  7%] 
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                                                                 [  9%] 
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                                                                      [ 11%] 
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                                                                      [ 14%] 
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                                                            [ 16%] 
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                                                             [ 19%] 
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                                                           [ 21%] 
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                                                             [ 23%] 
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                                                             [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                                                                        [ 28%] 
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                                                                    [ 30%] 
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                                                              [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                                                                     [ 35%] 
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                                                                         [ 38%] 
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                                                                   [ 40%] 
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                                                                         [ 42%] 
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                                                             [ 45%] 
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                                                               [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                                                                 [ 50%] 
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                                                                       [ 52%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                                                            [ 54%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                                                              [ 57%] 
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                                                                  [ 59%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                                                               [ 61%] 
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                                                                        [ 64%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                                                                       [ 66%] 
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                                                                  [ 69%] 
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                                                              [ 71%] 
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                                                                         [ 73%] 
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                                                             [ 76%] 
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                                                                   [ 78%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                                                             [ 80%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED                                                          [ 83%] 
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                                                                        [ 85%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                                                                       [ 88%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                                                           [ 90%] 
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                                                                      [ 92%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                                                               [ 95%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED                                                     [ 97%] 
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED                                                         [100%] 

========================================================================== 42 passed in 3.49s =========================================================================== 
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Outside, there is a downpour. | Outside, the rain is heavy. | high | 0.8732 | Có |
| 2 | The server crashed during deployment. | I had coffee this morning. | low | 0.1187  | Có |
| 3 | She is reading a book in the library. | A person is reading inside a library. | high | 0.8124 | Có |
| 4  | The system failed due to a timeout error. | A timeout caused the system to stop working. | high | 0.8469 | Có |
| 5  | The weather is extremely hot today. | The database query returned no results. | low | 0.0675 | Có |


**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Cặp 4 khá bất ngờ vì hai câu dùng từ khác nhau nhưng vẫn đạt similarity cao, cho thấy embeddings có khả năng bắt được quan hệ nguyên nhân–kết quả chứ không chỉ dựa vào từ giống nhau. Điều này cho thấy embeddings encode semantic meaning khá tốt, nhưng cũng có thể làm mờ ranh giới giữa các cách diễn đạt khác nhau.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Cách tính điểm cho bài tập UX Ngày 5 là gì? | Dựa trên tiêu chí trải nghiệm người dùng và tính khả thi (chi tiết trong day05.md). |
| 2 | Các giai đoạn chính của Lab Ngày 7 gồm những gì? | Gồm 2 Phase: Cá nhân (implement src) và Nhóm (benchmark strategy). |
| 3 | Deadline nộp SPEC draft là lúc mấy giờ? | Thường được quy định vào cuối ngày hoặc theo timeline trong day05.md. |
| 4 | Sự khác biệt giữa Mock prototype và Working prototype là gì? | Mock là bản mô phỏng giao diện, Working là bản có chức năng thực tế (day06.md). |
| 5 | Cấu trúc thư mục của Phase 3 yêu cầu gì? | Yêu cầu các folder src, tests và notebook rõ ràng (day03.md). |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Cách tính điểm cho bài tập UX Ngày 5 là gì? | Nội dung Ngày 5 nói về thiết kế sản phẩm AI cho uncertainty | 0.075 | Có | Mới chỉ cho thấy echo lại context về ngày 5, chưa có cách tính điểm |
| 2 | Các giai đoạn chính của Lab Ngày 7 gồm những gì? | Nội dung về Lab 3 (Chatbot vs ReAct Agent), không liên quan trực tiếp Lab Ngày 7 | 0.084 | Không | Trả lời dựa trên context sai (Lab 3), không nêu đúng các giai đoạn của Lab Ngày 7 |
| 3 | Deadline nộp SPEC draft là lúc mấy giờ? | Nội dung Ngày 6 (Hackathon, timeline sáng/chiều), có khả năng chứa thông tin deadline | 0.182 | Có | Trả lời dựa trên lịch Ngày 6 nhưng không trích xuất rõ thời gian deadline cụ thể |
| 4 | Sự khác biệt giữa Mock prototype và Working prototype là gì? | Nội dung Ngày 2 về problem statement, không liên quan đến prototype | 0.167 | Không | Trả lời dựa trên context sai (problem statement), không giải thích được sự khác biệt giữa hai loại prototype |
| 5 | Cấu trúc thư mục của Phase 3 yêu cầu gì? | Nội dung Day 3 (Lab 3, Phase 3 overview) | 0.029 | Có | Trả lời dựa trên mô tả tổng quan Phase 3, không nêu rõ yêu cầu cụ thể về cấu trúc thư mục |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Chỉ cần truyền thêm chunk_count khác vào kết quả số chunk và ava_length đã thay đổi đáng kể, và cả sự khác biệt giữa regex \n và không đối với SentenceChunker quan trọng thế nào.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Một số nhóm tập trung cải thiện retrieval bằng cách chọn chunking strategy phù hợp với domain thay vì dùng mặc định, cho thấy chất lượng dữ liệu đầu vào ảnh hưởng rất lớn đến kết quả của toàn hệ thống.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Lần sau tôi sẽ ưu tiên thử Sentence Chunking, hoặc thử nghiệm chunker và embedder model khác thay mock để xem sự khác biệt, có hiệu quả hơn không

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 13 / 15 |
| My approach | Cá nhân | 8 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 9 / 10 |
| Core implementation (tests) | Cá nhân | 29 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **90/ 100** |
