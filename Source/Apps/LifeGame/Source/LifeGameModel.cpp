#include <BraveNewWorld/LifeGame/LifeGameModel.hpp>

#include <algorithm>
#include <utility>

namespace brave_new_world::life_game
{
LifeGameModel::LifeGameModel()
    : LifeGameModel(DefaultSeed())
{
}

LifeGameModel::LifeGameModel(Seed seed)
    : m_seed(std::move(seed))
{
    for (Cell& cell : m_seed)
    {
        cell.row %= kRows;
        cell.column %= kColumns;
    }
    std::ranges::sort(
        m_seed,
        [](const Cell& left, const Cell& right)
        {
            return left.row < right.row ||
                   (left.row == right.row && left.column < right.column);
        });
    const auto duplicateBegin = std::ranges::unique(m_seed).begin();
    m_seed.erase(duplicateBegin, m_seed.end());
    Reset();
}

LifeGameModel::Seed LifeGameModel::DefaultSeed()
{
    return {
        {1U, 2U},
        {2U, 3U},
        {3U, 1U},
        {3U, 2U},
        {3U, 3U},
    };
}

void LifeGameModel::Reset() noexcept
{
    m_cells.fill(false);
    for (const Cell& cell : m_seed)
    {
        m_cells[Index(cell.row, cell.column)] = true;
    }
    m_generation = 0U;
    m_paused = true;
}

void LifeGameModel::Pause() noexcept
{
    m_paused = true;
}

void LifeGameModel::Resume() noexcept
{
    m_paused = false;
}

void LifeGameModel::TogglePaused() noexcept
{
    m_paused = !m_paused;
}

void LifeGameModel::SingleStep() noexcept
{
    Evolve();
}

bool LifeGameModel::Advance() noexcept
{
    if (m_paused)
    {
        return false;
    }
    Evolve();
    return true;
}

bool LifeGameModel::IsPaused() const noexcept
{
    return m_paused;
}

bool LifeGameModel::IsAlive(std::size_t row, std::size_t column) const noexcept
{
    return m_cells[Index(row % kRows, column % kColumns)];
}

std::uint64_t LifeGameModel::Generation() const noexcept
{
    return m_generation;
}

std::size_t LifeGameModel::LiveCount() const noexcept
{
    return static_cast<std::size_t>(std::ranges::count(m_cells, true));
}

const LifeGameModel::Storage& LifeGameModel::Cells() const noexcept
{
    return m_cells;
}

std::size_t LifeGameModel::Wrap(long long value, std::size_t extent) noexcept
{
    const auto signedExtent = static_cast<long long>(extent);
    const auto remainder = value % signedExtent;
    return static_cast<std::size_t>(remainder < 0 ? remainder + signedExtent : remainder);
}

std::size_t LifeGameModel::LiveNeighborCount(
    std::size_t row,
    std::size_t column) const noexcept
{
    std::size_t count = 0U;
    for (long long rowOffset = -1; rowOffset <= 1; ++rowOffset)
    {
        for (long long columnOffset = -1; columnOffset <= 1; ++columnOffset)
        {
            if (rowOffset == 0 && columnOffset == 0)
            {
                continue;
            }
            const auto neighborRow = Wrap(static_cast<long long>(row) + rowOffset, kRows);
            const auto neighborColumn =
                Wrap(static_cast<long long>(column) + columnOffset, kColumns);
            count += m_cells[Index(neighborRow, neighborColumn)] ? 1U : 0U;
        }
    }
    return count;
}

void LifeGameModel::Evolve() noexcept
{
    Storage next{};
    for (std::size_t row = 0U; row < kRows; ++row)
    {
        for (std::size_t column = 0U; column < kColumns; ++column)
        {
            const auto neighbors = LiveNeighborCount(row, column);
            const bool alive = m_cells[Index(row, column)];
            next[Index(row, column)] = neighbors == 3U || (alive && neighbors == 2U);
        }
    }
    m_cells = next;
    ++m_generation;
}
} // namespace brave_new_world::life_game
