---
type: knowledge
project: ivc_ai
topic: hardware
created: 2026-11-18
updated: 2026-11-18
tags: [knowledge, hardware, local_ai]
---

# Hardware Profile (ivc_ai)

> Закупка оформлена. Ожидается поставка.

## Спецификация

| Компонент | Модель | Ключевой параметр |
|-----------|--------|-------------------|
| CPU | AMD Ryzen 9 9900X | 12 ядер / 24 потока, Zen 5 |
| RAM | Silicon Power Xpower Zenith 64 GB DDR5 | UDIMM |
| GPU | ASUS RTX 5070 Ti PRIME OC | 16 GB VRAM GDDR7 |
| Storage | Kingston NV3 1 TB NVMe | M.2, модели + кэш |
| PSU | DeepCool PN1000D | 1000W, ATX 3.x |
| MB | ASUS PRIME B850-PLUS-CSM | AM5, DDR5 |
| Cooler | Arctic Freezer 36-S | Воздух |
| Case | Chieftec Night Hunter | ATX |

## Совместимость с Cyber-Tiel-Coder-35B-A3B

Модель: MoE 35B total / ~3B active params.

### Расчёт по VRAM (16 GB RTX 5070 Ti)

| Квантование | Вес файла | VRAM (оценка) | Влезает? | Рекомендация |
|-------------|----------|---------------|----------|--------------|
| Q4_K_M      | ~20 GB   | ~6-8 GB       | Да       | основной выбор |
| Q5_K_M      | ~24 GB   | ~8-10 GB      | Да       | если есть запас |
| Q6_K        | ~28 GB   | ~10-12 GB     | Да       | максимум качества |
| Q8_0        | ~35 GB   | ~14-16 GB     | На грани | только без контекста |

> MoE-модель загружает все веса в память, но активирует только ~3B.
> При 16 GB VRAM комфортно работают Q4_K_M – Q6_K с контекстом 8K+.
> Q8_0 возможен, но оставляет мало места под KV-cache.

### CPU Offload (резерв)

При нехватке VRAM часть слоёв уходит в RAM через llama.cpp/Ollama.
64 GB DDR5 + 12-ядерный 9900X позволяют offload без катастрофического падения скорости.
Ожидаемая скорость при частичном offload: 5-10 t/s (vs 30-50 t/s pure GPU).

### Storage

1 TB NVMe хватит на:
- OS + софт: ~100 GB
- Модели (3-4 квантования): ~100 GB
- Vault + чаты + RAG индекс: ~50 GB
- Резерв: ~750 GB

При необходимости добавить второй NVMe для моделей (B850 имеет несколько слотов M.2).

## Итоговая рекомендация

- Основное квантование: Q5_K_M (баланс качества и запаса VRAM)
- Резервное: Q4_K_M (для длинного контекста >8K)
- Эмбеддинги: bge-m3 FP16 (~2 GB VRAM, поместится вместе с основной моделью)

## Связанные

- [[hardware_procurement]]
- [[model_cyber_tiel_coder]]
- [[model_registry]]
