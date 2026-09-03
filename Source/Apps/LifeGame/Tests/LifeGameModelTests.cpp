#include <BraveNewWorld/LifeGame/LifeGameModel.hpp>

#include <cstdlib>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>

namespace
{
using brave_new_world::life_game::LifeGameModel;

void Require(bool condition, const std::string& message)
{
    if (!condition)
    {
        throw std::runtime_error{message};
    }
}

void RequireOnlyAlive(
    const LifeGameModel& model,
    const LifeGameModel::Seed& expected,
    const std::string& context)
{
    Require(model.LiveCount() == expected.size(), context + ": unexpected live count");
    for (const auto& cell : expected)
    {
        Require(model.IsAlive(cell.row, cell.column), context + ": expected cell is dead");
    }
}

void TestBlinker()
{
    LifeGameModel model{{{12U, 11U}, {12U, 12U}, {12U, 13U}}};
    model.SingleStep();
    RequireOnlyAlive(model, {{11U, 12U}, {12U, 12U}, {13U, 12U}}, "blinker step 1");
    model.SingleStep();
    RequireOnlyAlive(model, {{12U, 11U}, {12U, 12U}, {12U, 13U}}, "blinker step 2");
    Require(model.Generation() == 2U, "blinker generation must advance twice");
}

void TestGlider()
{
    LifeGameModel model{{{1U, 2U}, {2U, 3U}, {3U, 1U}, {3U, 2U}, {3U, 3U}}};
    for (int step = 0; step < 4; ++step)
    {
        model.SingleStep();
    }
    RequireOnlyAlive(
        model,
        {{2U, 3U}, {3U, 4U}, {4U, 2U}, {4U, 3U}, {4U, 4U}},
        "glider after period");
    Require(model.Generation() == 4U, "glider generation must advance four times");
}

void TestReset()
{
    const LifeGameModel::Seed seed{{7U, 7U}, {7U, 8U}, {7U, 9U}};
    LifeGameModel model{seed};
    model.Resume();
    Require(model.Advance(), "resumed model must advance");
    model.Reset();
    Require(model.Generation() == 0U, "reset must restore generation zero");
    Require(model.IsPaused(), "reset must restore the paused state");
    RequireOnlyAlive(model, seed, "reset seed");
}

void TestToroidalWrap()
{
    LifeGameModel model{{{0U, 23U}, {0U, 0U}, {0U, 1U}}};
    model.SingleStep();
    RequireOnlyAlive(model, {{23U, 0U}, {0U, 0U}, {1U, 0U}}, "toroidal blinker");
}

void TestPauseResumeAndSingleStep()
{
    LifeGameModel model{{{12U, 11U}, {12U, 12U}, {12U, 13U}}};
    Require(model.IsPaused(), "model must start paused");
    Require(!model.Advance(), "paused model must not advance");
    Require(model.Generation() == 0U, "paused generation must remain unchanged");
    model.SingleStep();
    Require(model.Generation() == 1U, "single-step must advance while paused");
    model.Resume();
    Require(model.Advance(), "resumed model must advance");
    model.Pause();
    Require(!model.Advance(), "paused model must stop again");
    Require(model.Generation() == 2U, "pause must retain the current generation");
}
} // namespace

int main()
{
    try
    {
        TestBlinker();
        TestGlider();
        TestReset();
        TestToroidalWrap();
        TestPauseResumeAndSingleStep();
        std::cout << "{\"schema\":\"brave-new-world-life-game-model-v1\","
                     "\"grid\":\"24x24\",\"rules\":\"B3/S23\",\"cases\":5,"
                     "\"passed\":true}\n";
        return EXIT_SUCCESS;
    }
    catch (const std::exception& exception)
    {
        std::cerr << "life-game model test failed: " << exception.what() << '\n';
        return EXIT_FAILURE;
    }
}
