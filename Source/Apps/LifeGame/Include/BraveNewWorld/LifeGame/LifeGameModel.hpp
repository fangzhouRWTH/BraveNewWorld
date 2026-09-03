#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace brave_new_world::life_game
{
class LifeGameModel final
{
public:
    static constexpr std::size_t kRows = 24U;
    static constexpr std::size_t kColumns = 24U;
    static constexpr std::size_t kCellCount = kRows * kColumns;

    struct Cell final
    {
        std::size_t row = 0U;
        std::size_t column = 0U;

        [[nodiscard]] bool operator==(const Cell&) const noexcept = default;
    };

    using Seed = std::vector<Cell>;
    using Storage = std::array<bool, kCellCount>;

    LifeGameModel();
    explicit LifeGameModel(Seed seed);

    [[nodiscard]] static Seed DefaultSeed();

    void Reset() noexcept;
    void Pause() noexcept;
    void Resume() noexcept;
    void TogglePaused() noexcept;
    void SingleStep() noexcept;
    [[nodiscard]] bool Advance() noexcept;

    [[nodiscard]] bool IsPaused() const noexcept;
    [[nodiscard]] bool IsAlive(std::size_t row, std::size_t column) const noexcept;
    [[nodiscard]] std::uint64_t Generation() const noexcept;
    [[nodiscard]] std::size_t LiveCount() const noexcept;
    [[nodiscard]] const Storage& Cells() const noexcept;

private:
    [[nodiscard]] static constexpr std::size_t Index(
        std::size_t row,
        std::size_t column) noexcept
    {
        return row * kColumns + column;
    }

    [[nodiscard]] static std::size_t Wrap(long long value, std::size_t extent) noexcept;
    [[nodiscard]] std::size_t LiveNeighborCount(
        std::size_t row,
        std::size_t column) const noexcept;
    void Evolve() noexcept;

    Seed m_seed;
    Storage m_cells{};
    std::uint64_t m_generation = 0U;
    bool m_paused = true;
};
} // namespace brave_new_world::life_game
